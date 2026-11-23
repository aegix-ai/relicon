"""Funnel model (D3): per step, Bayesian linear regression on the empirical logit with a pooling cascade
global -> vertical -> niche -> brand. Each level uses only its own data; the parent posterior, widened by
tau^2, is its prior, so no observation is counted twice."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..genome.models import Brief
from . import features
from .data import STEPS, Observation, emp_logit

PRIOR_SD, INTERCEPT_SD = 0.12, 2.0
TAU, TAU_INTERCEPT = 0.10, 0.5
SIGMA_AD0 = 0.2


@dataclass
class Gaussian:
    m: np.ndarray
    S: np.ndarray

    def widen(self, tau: float, tau0: float) -> "Gaussian":
        d = np.full(len(self.m), tau ** 2)
        d[0] = tau0 ** 2
        return Gaussian(self.m.copy(), self.S + np.diag(d))

    def update(self, X: np.ndarray, y: np.ndarray, var: np.ndarray) -> "Gaussian":
        if len(y) == 0:
            return self
        P0 = np.linalg.inv(self.S)
        W = 1.0 / var
        P = P0 + (X * W[:, None]).T @ X
        S = np.linalg.inv(P)
        S = (S + S.T) / 2
        m = S @ (P0 @ self.m + X.T @ (W * y))
        return Gaussian(m, S)


def prior(y_pool: np.ndarray | None) -> Gaussian:
    D = features.dim()
    m = np.zeros(D)
    m[0] = float(np.median(y_pool)) if y_pool is not None and len(y_pool) else -2.2
    sd = np.full(D, PRIOR_SD)
    sd[0] = INTERCEPT_SD
    return Gaussian(m, np.diag(sd ** 2))


def level_of(o: Observation, b: Brief) -> int:
    g = o.genome.brief
    if g.vertical != b.vertical:
        return 0
    if g.niche != b.niche:
        return 1
    if g.brand != b.brand:
        return 2
    return 3


@dataclass
class StepFit:
    post: Gaussian
    sigma_ad: float
    n_obs: int
    n_by_level: list[int]


class FunnelModel:
    def __init__(self, brief: Brief, observations: list[Observation], floor: int = 1000,
                 steps: tuple[str, ...] = STEPS):
        self.brief = brief
        self.obs = [o for o in observations if o.usable(floor)]
        self.excluded = len(observations) - len(self.obs)
        self.fits: dict[str, StepFit] = {}
        X = features.encode_many([o.genome for o in self.obs])
        lv = np.array([level_of(o, brief) for o in self.obs], dtype=int)
        for step in steps:
            s = np.array([o.counts[step][0] for o in self.obs], dtype=float)
            n = np.array([o.counts[step][1] for o in self.obs], dtype=float)
            keep = n > 0
            self.fits[step] = self._fit(X[keep], s[keep], n[keep], lv[keep])

    def _fit(self, X, s, n, lv) -> StepFit:
        y, vb = emp_logit(s, n) if len(s) else (np.zeros(0), np.zeros(0))
        sig2 = SIGMA_AD0 ** 2
        post = prior(y)
        for _ in range(3):  # alternate posterior and overdispersion estimate
            post = prior(y)
            for k in range(4):
                sel = lv == k
                post = post.update(X[sel], y[sel], vb[sel] + sig2)
                if k < 3:
                    post = post.widen(TAU, TAU_INTERCEPT)
            if len(y) < 8:
                break
            r = y - X @ post.m
            h = np.einsum("ij,jk,ik->i", X, post.S, X) / (vb + sig2)
            est = np.mean(r ** 2 / np.clip(1 - h, 0.05, 1) - vb)
            sig2 = float(np.clip(est, 0.05 ** 2, 0.6 ** 2))
        return StepFit(post, float(np.sqrt(sig2)), int(len(y)), [int((lv == k).sum()) for k in range(4)])

    # ---- prediction --------------------------------------------------------------------------
    def logits(self, X: np.ndarray, step: str) -> tuple[np.ndarray, np.ndarray]:
        f = self.fits[step]
        mu = X @ f.post.m
        sd = np.sqrt(np.einsum("ij,jk,ik->i", X, f.post.S, X))
        return mu, sd

    def draw(self, rng: np.random.Generator, step: str) -> np.ndarray:
        f = self.fits[step]
        return rng.multivariate_normal(f.post.m, f.post.S, method="cholesky")

    def score(self, X: np.ndarray, steps: tuple[str, ...], betas: dict[str, np.ndarray] | None = None) -> np.ndarray:
        """Sum of log rates over the objective's steps. For ROAS that is log(hook*click*cvr) + const."""
        tot = np.zeros(len(X))
        for st in steps:
            z = X @ (betas[st] if betas else self.fits[st].post.m)
            tot += -np.logaddexp(0, -z)
        return tot

    def uncertainty(self, X: np.ndarray, steps: tuple[str, ...]) -> np.ndarray:
        var = np.zeros(len(X))
        for st in steps:
            mu, sd = self.logits(X, st)
            p = 1 / (1 + np.exp(-mu))
            var += ((1 - p) * sd) ** 2
        return np.sqrt(var)

    def rates(self, X: np.ndarray) -> dict[str, np.ndarray]:
        return {st: 1 / (1 + np.exp(-(X @ self.fits[st].post.m))) for st in self.fits}
