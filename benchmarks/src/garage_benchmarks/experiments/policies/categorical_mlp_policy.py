"""Benchmarking experiment of the CategoricalMLPPolicy."""
import tensorflow as tf

from garage import wrap_experiment
from garage.envs import GymEnv, normalize
from garage.experiment import deterministic, LocalTFRunner
from garage.np.baselines import LinearFeatureBaseline
from garage.tf.algos import PPO
from garage.tf.policies import CategoricalMLPPolicy


@wrap_experiment
def categorical_mlp_policy(ctxt, env_id, seed):
    """Create Categorical MLP Policy on TF-PPO.

    Args:
        ctxt (garage.experiment.ExperimentContext): The experiment
            configuration used by LocalRunner to create the
            snapshotter.
        env_id (str): Environment id of the task.
        seed (int): Random positive integer for the trial.

    """
    deterministic.set_seed(seed)

    with LocalTFRunner(ctxt) as runner:
        env = normalize(GymEnv(env_id))

        policy = CategoricalMLPPolicy(
            env_spec=env.spec,
            hidden_nonlinearity=tf.nn.tanh,
        )

        baseline = LinearFeatureBaseline(env_spec=env.spec)

        algo = PPO(env_spec=env.spec,
                   policy=policy,
                   baseline=baseline,
                   discount=0.99,
                   gae_lambda=0.95,
                   lr_clip_range=0.2,
                   policy_ent_coeff=0.0,
                   optimizer_args=dict(
                       batch_size=32,
                       max_episode_length=10,
                       learning_rate=1e-3,
                   ),
                   name='CategoricalMLPPolicyBenchmark')

        runner.setup(algo, env, sampler_args=dict(n_envs=12))
        runner.train(n_epochs=5, batch_size=2048)
