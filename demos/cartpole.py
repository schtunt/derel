#!/usr/bin/env python3
import random

import gym
import typing
import types

Action = typing.TypeVar('Action')
class ActionWrapper(gym.ActionWrapper):
    def __init__(self, env, action_fn, epsilon=0.1):
        super(self.__class__, self).__init__(env)
        self.epsilon = epsilon
        self.action = types.MethodType(action_fn, self)

    def action(self, action:Action) -> Action:
        raise Exception('Undefined')

def main():
    env = gym.make('CartPole-v0')

    def _action_fn(self, action:Action) -> Action:
        if random.random() < self.epsilon:
            return self.env.action_space.sample()
        return action
    env = ActionWrapper(env, _action_fn)
    env = gym.wrappers.Monitor(env, "recording", force=True)

    reward_counter = 0.0
    step_counter = 0
    obs = env.reset()

    while True:
        action = env.action_space.sample()
        obs, reward, done, _ = env.step(action)
        reward_counter += reward
        step_counter += 1

        if done:
            break

    print("steps:%d, rewards:%0.2f" % ( step_counter, reward_counter ))

if __name__ == '__main__':
    main()
