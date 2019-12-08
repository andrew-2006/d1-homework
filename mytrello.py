import sys 
import requests  

base_url = "https://api.trello.com/1/{}" 
auth_params = {    
    'key': "ef03b49e4b07a0baf492034b1ccf3339",    
    'token': "117d49bd031d2d3d067b5191e615c677471309e63582b5c591a560295c79975e", }
board_id = "z6ohfuBU" 
response = requests.get(base_url.format('boards/' + board_id), params=auth_params).json() # Длинный ID
column_data = requests.get(base_url.format('boards') + '/' + board_id)
print(base_url.format('boards'))
print(column_data)

def read():      
    # Получим данные всех колонок на доске:      
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()      
      
    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:      
    for column in column_data:      
            
        # Получим данные всех задач в колонке и перечислим все названия      
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()  
        print(column['name'] + " - ({})".format(len(task_data)))
     
        if not task_data:      
            print('\t' + 'Нет задач!')      
            continue      
        for task in task_data:  
            print('\t' + task['name'] + '\t' + task['id'])
    
def create(name, column_name):      
    # Получим данные всех колонок на доске      
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()      
      
    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна      
    for column in column_data:      
        if column['name'] == column_name:      
            # Создадим задачу с именем _name_ в найденной колонке      
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})      
	    break

    column_id = column_check(column_name)  
    if column_id is None:  
        column_id = create_column(column_name)['id']  
  
    requests.post(base_url.format('cards'), data={'name': name, 'idList': column_id, **auth_params})  
    
def move(name, column_name):    
    # Получим данные всех колонок на доске    
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()    
    
    duplicate_tasks = get_task_duplicates(name)  
    if len(duplicate_tasks) > 1:  
        print("Задач с таким названием несколько штук:")  
        for index, task in enumerate(duplicate_tasks):  
            task_column_name = requests.get(base_url.format('lists') + '/' + task['idList'], params=auth_params).json()['name']  
            print("Задача №{}\tid: {}\tНаходится в колонке: {}\t ".format(index, task['id'], task_column_name))  
        task_id = input("Пожалуйста, введите ID задачи, которую нужно переместить: ")  
    else:  
        task_id = duplicate_tasks[0]['id']
    
    # Среди всех колонок нужно найти задачу по имени и получить её id  
    task_id = None  
    for column in column_data:  
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()  
        for task in column_tasks:  
            if task['name'] == name:  
                task_id = task['id']  
                break  
        if task_id:  
            break  
  
    # Теперь, когда у нас есть id задачи, которую мы хотим переместить,  
    # Получим ID колонки, в которую мы будем перемещать задачу  column_id = column_check(column_name)  
    if column_id is None:  
        column_id = create_column(column_name)['id']  
    # И совершим перемещение:  
    requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column_id, **auth_params})

def create_column(column_name):  
    return requests.post(base_url.format('lists'), data={'name': column_name, 'idBoard': board_id_long, **auth_params}).json()   

# Функция проверки существования колонки
def column_check(column_name):  
    column_id = None  
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()  
    for column in column_data:  
        if column['name'] == column_name:  
            column_id = column['id']  
            return column_id

def get_task_duplicates(task_name):  
    # Получим данные всех колонок на доске  
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()  
  
    # Заведём список колонок с дублирующимися именами  
    duplicate_tasks = []  
    for column in column_data:  
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()  
        for task in column_tasks:  
            if task['name'] == task_name:  
                duplicate_tasks.append(task)  
    return duplicate_tasks
    
if __name__ == "__main__":    
    if len(sys.argv) <= 2:    
        read()    
    elif sys.argv[1] == 'create':    
        create(sys.argv[2], sys.argv[3])    
    elif sys.argv[1] == 'move':    
        move(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_column':
        create_column(sys.argv[2])