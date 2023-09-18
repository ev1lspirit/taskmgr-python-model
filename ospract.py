import sys
import heapq
import re
from random import randint

ROOT = 0


# Объект процесса Task.
class Task:

	"""
	Объект процесса Task.
	Процесс содержит себе следующие поля:

	public:
		name - имя процесса
		start_tick - время старта процесса
		duration - длительность выполнения процесса
		priority - приоритет, заданный процессу

	private:
		_executor_object - объект генератора Python, имитирующий выполнение процесса
		_ratio - коэффициент согласно заданию
		_start_priority - начальный приоритет процесса

	"""

	__slots__ = ("name", "start_tick", "duration", "priority", "current_tick", "_executor_object", "_ratio",
				"_start_priority")

	def __init__(self, *, name, start_tick, duration, priority):
		self.name = name
		self.start_tick = start_tick
		self.duration = duration
		self.priority = priority
		self._start_priority = self.priority
		self.current_tick = 0
		self._ratio = 0.01
		self._set_executor()

	@staticmethod
	def get_empty_task():
		return Task(name="-", start_tick=0, duration=sys.maxsize, priority=-1)

	# создает генератор для имитации выполнения процесса
	def _set_executor(self):
		self._executor_object = self._do_execution()
	
	def __repr__(self):
		return f"Task(name={self.name}, start_tick={self.start_tick},duration={self.duration}, priority={self.priority}, current_tick={self.current_tick})"

	# имитация выполнения процесса
	def _do_execution(self):
		yield from range(self.duration-1)

	def tick(self):
		self.current_tick = next(self._executor_object, False)
		return self.current_tick

	# проверка, завершился ли процесс или нет
	def finished(self):
		return True if self.current_tick is False else False

	# меняет приоритет процесса согласно формуле из варианта
	def reset_priority(self, tick):
		if self.name == "-":
			return
		self.priority = round(self._start_priority * self._ratio * tick * tick * tick)


class PriorityQueue:
	"""
		Очередь с приоритетом.
		Очередь реализована на основе структуры данных heap ("куча")
		- отсортированного по возрастанию или убыванию бинарного дерева

		Методы:
			push(task: Task) - добавляет процесс в кучу на основе приоритета (1-ая очередь)
				и времени начала выполнения (2-ая очередь)

			pop() - удаляет процесс из кучи
	"""
	def __init__(self):
		self._queue = []
		self._index = 0
			
	def push(self, task: Task):
		heapq.heappush(self._queue, (-task.priority, task.start_tick, self._index, task))
		self._index += 1
			
	def pop(self):
		return heapq.heappop(self._queue)[-1]
			
	def __len__(self):
		return len(self._queue)

	def __getitem__(self, item):
		if not isinstance(item, int):
			raise TypeError(f'Expected int, got {type(item).__name__} instead')
		return self._queue[item]


# Автоматическое создание име процессов в пределах от A ДО Z
all_possible_names = set(map(chr, range(65, 91)))

# Пустой процесс. Если у диспетчера задач нету текущих процессовб но имеются запланированные позже -
# данный процесс появляется во время ожидания
empty_task = Task.get_empty_task()


# генератор, создающий объект процесса автоматически
def _create_processes(tasks_amount_):
	for _, name in zip(range(tasks_amount_), all_possible_names):
		yield Task(name=name, start_tick=randint(0, 6), duration=randint(1, 6), priority=randint(0, 6))


# количество задач для диспетчеризации
# вводится с клавиатуры и парсится с помощью регулярного выражения
input_value = re.match(r"(\d+)", input("Введите число процессов для диспетчеризации: "))

# если введенное число не распознано - для диспетчеризации выбираются все задачи из списка tasks
if not input_value:
	tasks_amount = len(all_possible_names)
else:
	digit = int(input_value.group(1))
	tasks_amount = digit if digit < len(all_possible_names) else len(all_possible_names)

# описание процессов
tasks = list(task for task in _create_processes(tasks_amount))


# Имена процессов, выбранных для диспетчеризации.
# Пока нижепривиденное множество не пусто - событийный цикл выполняется
tasks_set = set(task.name for task in tasks if task != empty_task)


tab = "\t"
print(f"Имя процесса{tab*3}Время начала выполнения{tab*3}Длительность выполненияt{tab*3}Приоритет")
for task in tasks:
	if task != empty_task:
		print(f"{task.name}{tab*9}{task.start_tick}{tab*7}{task.duration}{tab*8}{task.priority}")


# Предварительная сортировка процессов по времени начала исполнения (1-ая очередь)
# и приоритету (2-ая очередь)
tasks.sort(key=lambda task: (task.start_tick, -task.priority))


# Функция выбора подходящего кандидата для выполнения
def _get_candidate(tasks_list: list[Task], heap: PriorityQueue):
	if not tasks_list and heap:
		return heap.pop()
	elif not heap and tasks_list:
		return tasks_list.pop(0)
	elif heap and tasks_list:
		highest_priority_task = tasks_list[0]
		*_, highest_awaiting = heap[0]
		if highest_priority_task.priority > highest_awaiting.priority:
			return tasks_list.pop(0)
		return heap.pop()
	else:
		return empty_task


# Событийный цикл
def event_loop(tasks_amount: int):
	# Функция, изменяющая приоритет раз в 3 такта
	def _try_reset_task_priority():
		if (tick + 1) % reset_interval == 0:
			past_priority = current_task.priority
			current_task.reset_priority(tick)
			resets.append(f"Приоритет процесса {current_task.name} изменился с {past_priority} "
						  f"до {current_task.priority} на такте {tick}")

	if tasks_amount < 1:
		return

	# Инициализация переменных
	reset_interval = 3   				# интервал смены приоритета
	tick = 0             				# такт процессора
	waiting_list = PriorityQueue()      # Очередь с приоритетом
	current_task = next(filter(lambda task: task.start_tick == tasks[ROOT].start_tick, tasks)) # поиск открывающего процесса
	if current_task.start_tick > 0:
		current_task = empty_task
	resets = []

	print("Номер такта\t\t\t\tCPU\t\t\t\tГотовновтсь")
	while tasks_set:

		# Выжимка неактивных процессов, готовых к обработке
		ready_to_execute = list(filter(lambda task: task.start_tick == tick and task != current_task, tasks))

		# Поиск подходящего кандидата среди выжимки неактивных процессов, готовых к обработке
		# и процессов, ожидающих выполнения в очереди
		candidate = _get_candidate(ready_to_execute, waiting_list)

		# Если текущий процесс закончен - выбрать наилучшего кандидата и собрать статистику о завершившемся процессе
		if current_task.finished():
			tasks_set.remove(current_task.name)
			if not tasks_set:
				break
			current_task = candidate
			_try_reset_task_priority()

		# Иначе - если среди выжимки неактивных процессов или зоны ожидания
		# есть найденный кандидат, который имеет больший приоритет
		# - этот процесс становится активным, а предыдущий активный процесс помещается в зону ожидания
		# Если же таких процессов нет, кандидат помещается/возвращается в зону ожидания
		else:
			if candidate.priority > current_task.priority:
				if current_task != empty_task:
					waiting_list.push(current_task)
				current_task = candidate
				_try_reset_task_priority()
			else:
				_try_reset_task_priority()
				if candidate != empty_task:
					waiting_list.push(candidate)

		# Поместить всю остальную выжимку в зону ожидания
		for task in ready_to_execute:
			waiting_list.push(task)

		print(tick, end="\t\t\t\t\t\t")
		print(current_task.name, end="\t\t\t\t\t")
		print(list(task.name for *_, task in waiting_list._queue))

		current_task.tick()
		tick += 1

	for reset in resets:
		print(reset)


# Передача количества задач для диспетчеризации в событийный цикл
event_loop(tasks_amount)

