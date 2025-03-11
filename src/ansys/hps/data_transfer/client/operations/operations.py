# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



class OperationInfo(object):
    def __init__(
        self,
        target
    ):
        self.target = target if target is None or isinstance(target, list) else [target]
        """Basic object describing an operation requested by the user. Must be pickable so as to make
        it across to another process.
        """
        # The two below are for internal use by the operation tracker and will have shared values assigned by it.
        self.num_tasks = None
        self.num_completed_tasks = None

    def prepare_progress(self, num_tasks):
        """Set the total amount of tasks that is to be used for calculating progress"""
        if self.num_tasks is None or self.num_completed_tasks is None:
            return
        self.num_tasks.value = num_tasks
        self.num_completed_tasks.value = 0

    def increase_progress(self, value=1):
        """Increase the count of completed tasks"""
        if self.num_completed_tasks is None:
            return

        self.num_completed_tasks.value += value

        # Here to prevent overflow.
        if self.num_completed_tasks.value > self.num_tasks.value:
            self.num_completed_tasks.value = self.num_tasks.value

    def increase_total(self, value=1):
        if self.num_tasks is None:
            return
        self.num_tasks.value += value