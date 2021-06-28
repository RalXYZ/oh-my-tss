import copy

import numpy as np
from numpy.random import rand


class Schedule:
    def __init__(self, sectionId, courseId, classId, teacherId, duration, compulsory_list, capacity, term):
        self.sectionId = sectionId
        self.courseId = courseId
        self.classId = classId
        self.teacherId = teacherId
        self.duration = duration
        self.compulsory_list = compulsory_list  # compulsory or not
        self.capacity = capacity
        self.term = term
        # print(courseId, classId, teacherId)
        self.roomId = 0
        self.roomIndex = -1
        self.campusId = 0
        self.weekDay = 0
        # 需要课程duration
        # slot：1~13其中某一节
        self.slot = 0

    def random_init(self, roomRange):
        # roomId从数据库现有数据随机选择一个
        random_num = int(np.random.randint(0, roomRange.count(), 1)[0])
        self.roomId = roomRange[random_num].id
        self.roomIndex = random_num
        # campus就是上面room所在的campus
        self.campusId = roomRange[random_num].campus_id
        self.weekDay = np.random.randint(1, 8, 1)[0]
        if self.duration == 1:
            self.slot = np.random.randint(1, 14, 1)[0]
        elif self.duration == 2:
            self.slot = [1, 3, 6, 7, 9, 11][np.random.randint(0, 6, 1)[0]]
        elif self.duration == 3:
            self.slot = [3, 6, 11][np.random.randint(0, 3, 1)[0]]


def schedule_cost(population, elite, roomRange):
    conflicts = []
    # conflicts用于存储population里面每个p的冲突值
    n = len(population[0])
    for p in population:
        conflict = 0
        for i in range(0, n):  # 教室容量不足
            capacity = roomRange[p[i].roomIndex].capacity
            if p[i].capacity > capacity:
                conflict += 1 * 1000
            # 尽量避免教室容量远大于课程容量
            elif p[i].capacity < capacity - 30:
                conflict += 1 * 100
            # 尽量不排在周末
            if p[i].weekDay == 6 or p[i].weekDay == 7:
                conflict += 1 * 250
            if (p[i].duration == 2 and p[i].slot not in {1, 3, 6, 7, 9, 11}) or \
                    (p[i].duration == 3 and p[i].slot not in {3, 6, 11}):
                conflict += 1000
            for j in range(i + 1, n):
                # 教室&时段冲突
                if p[i].roomId == p[j].roomId and p[i].weekDay == p[j].weekDay and \
                        not (p[i].slot + p[i].duration - 1 < p[j].slot or p[j].slot + p[j].duration - 1 < p[i].slot):
                    conflict += 1 * 1000
                # 同一门课的两个时段不能冲突
                if p[i].classId == p[j].classId and p[i].weekDay == p[j].weekDay and \
                        not (p[i].slot + p[i].duration - 1 < p[j].slot or p[j].slot + p[j].duration - 1 < p[i].slot):
                    conflict += 1 * 1000
                # 一个老师在某个时间段同时上两门课
                if p[i].teacherId == p[j].teacherId and p[i].weekDay == p[j].weekDay and \
                        not (p[i].slot + p[i].duration - 1 < p[j].slot or p[j].slot + p[j].duration - 1 < p[i].slot):
                    conflict += 1 * 1000
                # 同一个专业的必修课尽量不冲突
                if p[i].compulsory_list and p[j].compulsory_list:
                    for major in p[i].compulsory_list:
                        if major in p[j].compulsory_list and p[i].weekDay == p[j].weekDay and \
                                not (p[i].slot + p[i].duration - 1 < p[j].slot or p[j].slot + p[j].duration - 1 < p[
                                    i].slot):
                            conflict += 1 * 250
                            break
                # 同一门课程的两个时段不能跑校区
                if p[i].classId == p[j].classId and p[i].campusId != p[j].campusId:
                    conflict += 1000
                # 一个老师同一天的课尽量不跑校区
                if p[i].teacherId == p[j].teacherId and p[i].classId != p[j].classId \
                        and p[i].campusId != p[j].campusId and p[i].weekDay == p[j].weekDay:
                    conflict += 250
        conflicts.append(conflict)  # 末尾加值
    # index：conflicts按照从小到大排序的索引值
    index = np.array(conflicts).argsort()
    return index[: elite], conflicts[index[0]]


class GeneticOptimize:
    def __init__(self, popsize=10, mutprob=0.3, elite=8, maxiter=500):
        # 种群的规模（0-100）
        self.popsize = popsize
        # 变异概率
        self.mutprob = mutprob
        # 精英个数
        self.elite = elite
        # 进化代数（100-500）
        self.maxiter = maxiter

    # 随机初始化不同的种群
    def init_population(self, schedules, roomRange):
        self.population = []
        for i in range(self.popsize):
            entity = []
            for s in schedules:
                s.random_init(roomRange)
                # deepcopy产生的课程安排方案不会随着s的改变而变化
                entity.append(copy.deepcopy(s))
            self.population.append(entity)

    # 变异
    def mutate(self, eiltePopulation, roomRange, slotnum):
        # 选择变异的个数
        e = np.random.randint(0, self.elite, 1)[0]
        ep = copy.deepcopy(eiltePopulation[e])
        # 随机选择染色体的一段进行变异
        for p in ep:
            pos = np.random.randint(0, 3, 1)[0]
            if pos == 0:  # 改成随机选一个roomId
                p.roomId = self.change_room(roomRange)
                for i in range(0, roomRange.count()):
                    if roomRange[i].id == p.roomId:
                        p.campusId = roomRange[i].campus_id
                        p.roomIndex = i
                        break
            elif pos == 1:
                p.weekDay = self.change(p.weekDay, 7)
            elif pos == 2:
                p.slot = self.change_slot(p.duration)
        return ep

    def change_room(self, roomRange):
        roomId = roomRange[int(np.random.randint(0, roomRange.count(), 1)[0])].id
        return roomId

    def change_slot(self, duration):
        if duration == 1:
            value = np.random.randint(1, 14, 1)[0]
        elif duration == 2:
            value = [1, 3, 6, 7, 9, 11][np.random.randint(0, 6, 1)[0]]
        elif duration == 3:
            value = [3, 6, 11][np.random.randint(0, 3, 1)[0]]
        return value

    def change(self, value, valueRange):
        value = np.random.randint(1, valueRange + 1, 1)[0]
        # value=(value)%valueRange+1
        return value

    def crossover(self, eiltePopulation):
        # 随机从精英个体选择e1，e2
        e1 = np.random.randint(0, self.elite, 1)[0]
        e2 = np.random.randint(0, self.elite, 1)[0]
        # 随机决定交叉位置
        pos = np.random.randint(0, 3, 1)[0]
        ep1 = copy.deepcopy(eiltePopulation[e1])
        ep2 = eiltePopulation[e2]
        for p1, p2 in zip(ep1, ep2):
            if pos == 0:
                p1.weekDay = p2.weekDay
            if pos == 1:
                p1.roomId = p2.roomId
                p1.campusId = p2.campusId
            if pos == 2:
                p1.slot = p2.slot
        return ep1

    def evolution(self, schedules, roomRange, slotnum):
        bestSchedule = None
        self.init_population(schedules, roomRange)
        for i in range(self.maxiter):
            # eliteindex：筛选的精英种群
            eliteIndex, bestScore = schedule_cost(self.population, self.elite, roomRange)
            print('Iter: {} | conflict: {}'.format(i + 1, bestScore))
            if bestScore == 0 or i == self.maxiter - 1:  # 没有冲突
                bestSchedule = self.population[eliteIndex[0]]
                break
            newPopulation = [self.population[index] for index in eliteIndex]
            while len(newPopulation) < self.popsize:  # 增加人口
                if np.random.rand() < self.mutprob:
                    newp = self.mutate(newPopulation, roomRange, slotnum)
                else:
                    newp = self.crossover(newPopulation)
                newPopulation.append(newp)
            self.population = newPopulation
        return bestSchedule
