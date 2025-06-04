from Model import Schedule
import random
from random import randrange
import time
import matplotlib.pyplot as plt


# Генетический алгоритм
class GeneticAlgorithm:
    def initAlgorithm(
        self, prototype, numberOfChromosomes=100, replaceByGeneration=8, trackBest=5
    ):
        # Количество лучших хромосом, сохранённых в группе лучших хромосом
        self._currentBestSize = 0
        # Прототип хромосом в популяции
        self._prototype = prototype

        # В популяции должно быть не менее 2 хромосом
        if numberOfChromosomes < 2:
            numberOfChromosomes = 2

        # И алгоритм должен отслеживать хотя бы одну из лучших хромосом
        if trackBest < 1:
            trackBest = 1

        # Популяция хромосом
        self._chromosomes = numberOfChromosomes * [None]
        # Указывает, принадлежит ли хромосома группе лучших
        self._bestFlags = numberOfChromosomes * [False]

        # Индексы лучших хромосом
        self._bestChromosomes = trackBest * [0]
        # Количество хромосом, заменяемых в каждом поколении потомками
        self.set_replace_by_generation(replaceByGeneration)

    # Инициализирует генетический алгоритм
    def __init__(
        self,
        configuration,
        numberOfCrossoverPoints=2,
        mutationSize=2,
        crossoverProbability=80,
        mutationProbability=12,
    ):
        self.initAlgorithm(Schedule.Schedule(configuration))
        self._mutationSize = mutationSize
        self._numberOfCrossoverPoints = numberOfCrossoverPoints
        self._crossoverProbability = crossoverProbability
        self._mutationProbability = mutationProbability

    @property
    # Возвращает указатель на лучшие хромосомы в популяции
    def result(self):
        return self._chromosomes[self._bestChromosomes[0]]

    def set_replace_by_generation(self, value):
        numberOfChromosomes = len(self._chromosomes)
        trackBest = len(self._bestChromosomes)
        if value > numberOfChromosomes - trackBest:
            value = numberOfChromosomes - trackBest
        self._replaceByGeneration = value

    # Пытается добавить хромосому в группу лучших
    def addToBest(self, chromosomeIndex):
        bestChromosomes = self._bestChromosomes
        length_best = len(bestChromosomes)
        bestFlags = self._bestFlags
        chromosomes = self._chromosomes

        # Не добавлять, если новая хромосома не обладает достаточной приспособленностью
        # или уже находится в группе
        if (
            self._currentBestSize == length_best
            and chromosomes[bestChromosomes[self._currentBestSize - 1]].fitness
            >= chromosomes[chromosomeIndex].fitness
        ) or bestFlags[chromosomeIndex]:
            return

        # Найти место для новой хромосомы
        j = self._currentBestSize
        for i in range(j, -1, -1):
            j = i
            pos = bestChromosomes[i - 1]
            # Группа ещё не заполнена?
            if i < length_best:
                # Найдена позиция для новой хромосомы?
                if chromosomes[pos].fitness > chromosomes[chromosomeIndex].fitness:
                    break

                # Сдвинуть хромосомы, чтобы освободить место
                bestChromosomes[i] = pos
            else:
                # Группа заполнена, удалить худшую хромосому
                bestFlags[pos] = False

        # Сохранить хромосому в группе лучших
        bestChromosomes[j] = chromosomeIndex
        bestFlags[chromosomeIndex] = True

        # Увеличить текущий размер, если лимит ещё не достигнут
        if self._currentBestSize < length_best:
            self._currentBestSize += 1

    # Возвращает TRUE, если хромосома принадлежит группе лучших
    def isInBest(self, chromosomeIndex) -> bool:
        return self._bestFlags[chromosomeIndex]

    # Очищает группу лучших хромосом
    def clearBest(self):
        self._bestFlags = len(self._bestFlags) * [False]
        self._currentBestSize = 0

    # Инициализирует новую популяцию случайно сгенерированными хромосомами
    def initialize(self, population):
        prototype = self._prototype
        length_chromosomes = len(population)

        for i in range(0, length_chromosomes):
            # Добавить новую хромосому в популяцию
            population[i] = prototype.makeNewFromPrototype()

    def selection(self, population):
        length_chromosomes = len(population)
        return (
            population[randrange(32768) % length_chromosomes],
            population[randrange(32768) % length_chromosomes],
        )

    def replacement(self, population, replaceByGeneration) -> list:
        mutationSize = self._mutationSize
        numberOfCrossoverPoints = self._numberOfCrossoverPoints
        crossoverProbability = self._crossoverProbability
        mutationProbability = self._mutationProbability
        selection = self.selection
        isInBest = self.isInBest
        length_chromosomes = len(population)
        # Производит потомков
        offspring = replaceByGeneration * [None]
        for j in range(replaceByGeneration):
            # Случайно выбирает родителей
            parent = selection(population)

            offspring[j] = parent[0].crossover(
                parent[1], numberOfCrossoverPoints, crossoverProbability
            )
            offspring[j].mutation(mutationSize, mutationProbability)

            # Заменяет хромосомы текущей операции потомками
            # Случайно выбирает хромосому для замены
            ci = randrange(32768) % length_chromosomes
            while isInBest(ci):
                ci = randrange(32768) % length_chromosomes

            # Заменить хромосому
            population[ci] = offspring[j]

            # Попытаться добавить новую хромосому в группу лучших
            self.addToBest(ci)
        return offspring

    # Запускает и выполняет алгоритм
    def run(self, maxRepeat=9999, minFitness=0.999, maxGeneration=5000):
        # Очищает группу лучших хромосом от предыдущего выполнения
        self.clearBest()
        length_chromosomes = len(self._chromosomes)

        self.initialize(self._chromosomes)
        random.seed(round(time.time() * 1000))

        # Текущее поколение
        currentGeneration = 0

        # Список для хранения значений fitness
        fitness_history = []

        repeat = 0
        lastBestFit = 0.0

        while 1:
            best = self.result
            current_fitness = best.fitness
            print(
                "Fitness:",
                "{:f}\t".format(best.fitness),
                "Generation:",
                currentGeneration,
                end="\r",
            )

            # Сохраняем значение fitness
            fitness_history.append(current_fitness)

            # Алгоритм достиг цели?
            if best.fitness > minFitness:
                break

            if currentGeneration > maxGeneration:
                break

            difference = abs(best.fitness - lastBestFit)
            if difference <= 0.0000001:
                repeat += 1
            else:
                repeat = 0

            if repeat > (maxRepeat / 100):
                self.set_replace_by_generation(self._replaceByGeneration * 3)
                self._crossoverProbability += 1

            self.replacement(self._chromosomes, self._replaceByGeneration)

            lastBestFit = best.fitness
            random.seed(round(time.time() * 1000))
            currentGeneration += 1

        return {
            "fitness_history": fitness_history,
            "currentGeneration": currentGeneration
        }

    def __str__(self):
        return "Genetic Algorithm"