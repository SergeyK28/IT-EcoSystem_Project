# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server import db_crm


def get_objectives(status: str = 'active', filter_type: str = 'Все задачи',
                   search: str = '', employee_id: int = None) -> List[Dict[str, Any]]:
    """
    Получает список задач

    Args:
        status: Статус задач ('active', 'completed')
        filter_type: Тип фильтрации
        search: Поисковый запрос
        employee_id: ID текущего сотрудника

    Returns:
        Список задач
    """
    connection = db_crm.get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            o.ObjectiveID,
            o.EmployeeID,
            o.AssignedToID,
            o.OrderID,
            o.Title,
            o.Description,
            o.Status,
            o.Priority,
            o.DueDate,
            o.CompletedDate,
            o.CreatedDate,
            o.UpdatedDate,
            CONCAT(creater.FirstName, ' ', creater.LastName) as CreatedByName,
            CONCAT(assigned.FirstName, ' ', assigned.LastName) as AssignedToName,
            ord.OrderNumber as OrderNumber,
            CONCAT(ord.DeviceBrand, ' ', ord.DeviceModel) as OrderInfo
        FROM Objectives o
        LEFT JOIN ListEmployee creater ON o.EmployeeID = creater.EmployeeID
        LEFT JOIN ListEmployee assigned ON o.AssignedToID = assigned.EmployeeID
        LEFT JOIN Orders ord ON o.OrderID = ord.OrderID
        WHERE o.Status = %s
        """

        params = [status]

        # Применяем фильтры
        if filter_type == "Мои задачи" and employee_id:
            query += " AND o.EmployeeID = %s"
            params.append(employee_id)
        elif filter_type == "Назначенные мне" and employee_id:
            query += " AND o.AssignedToID = %s"
            params.append(employee_id)
        elif filter_type == "По заказам":
            query += " AND o.OrderID IS NOT NULL"
        elif filter_type == "Просроченные" and status == 'active':
            query += " AND o.DueDate < NOW()"

        # Поиск по тексту
        if search:
            query += """ AND (o.Title LIKE %s OR o.Description LIKE %s)"""
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])

        query += " ORDER BY "
        if status == 'active':
            query += "CASE WHEN o.DueDate < NOW() THEN 0 ELSE 1 END, o.DueDate ASC, o.Priority DESC"
        else:
            query += "o.CompletedDate DESC"

        cursor.execute(query, params)
        objectives = cursor.fetchall()

        # Для каждой задачи загружаем чеклист
        for obj in objectives:
            cursor.execute("""
                SELECT ChecklistID, ItemText, IsCompleted, OrderIndex
                FROM ObjectiveChecklist
                WHERE ObjectiveID = %s
                ORDER BY OrderIndex
            """, (obj['ObjectiveID'],))
            obj['Checklist'] = cursor.fetchall()

        return objectives

    except Error as e:
        print(f"Ошибка получения задач: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def create_objective(task_data: Dict[str, Any]) -> Optional[int]:
    """
    Создает новую задачу

    Args:
        task_data: Данные задачи

    Returns:
        ID созданной задачи или None
    """
    connection = db_crm.get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO Objectives (
            EmployeeID, AssignedToID, OrderID, Title, Description, Priority, DueDate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            task_data.get('employee_id'),
            task_data.get('assigned_to_id'),
            task_data.get('order_id'),
            task_data.get('title'),
            task_data.get('description'),
            task_data.get('priority', 'medium'),
            task_data.get('due_date')
        ))

        new_objective_id = cursor.lastrowid
        connection.commit()
        return new_objective_id

    except Error as e:
        print(f"Ошибка создания задачи: {e}")
        connection.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def update_objective_status(objective_id: int, status: str) -> bool:
    """
    Обновляет статус задачи

    Args:
        objective_id: ID задачи
        status: Новый статус

    Returns:
        True если успешно
    """
    connection = db_crm.get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        if status == 'completed':
            cursor.execute("""
                UPDATE Objectives 
                SET Status = %s, CompletedDate = NOW()
                WHERE ObjectiveID = %s
            """, (status, objective_id))
        else:
            cursor.execute("""
                UPDATE Objectives 
                SET Status = %s, CompletedDate = NULL
                WHERE ObjectiveID = %s
            """, (status, objective_id))

        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"Ошибка обновления статуса задачи: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def update_objective_description(objective_id: int, description: str) -> bool:
    """
    Обновляет описание задачи

    Args:
        objective_id: ID задачи
        description: Новое описание

    Returns:
        True если успешно
    """
    connection = db_crm.get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE Objectives 
            SET Description = %s
            WHERE ObjectiveID = %s
        """, (description, objective_id))

        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"Ошибка обновления описания задачи: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def delete_objective(objective_id: int) -> bool:
    """
    Удаляет задачу

    Args:
        objective_id: ID задачи

    Returns:
        True если успешно
    """
    connection = db_crm.get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM Objectives WHERE ObjectiveID = %s", (objective_id,))
        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"Ошибка удаления задачи: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_objective_comments(objective_id: int) -> List[Dict[str, Any]]:
    """
    Получает комментарии к задаче

    Args:
        objective_id: ID задачи

    Returns:
        Список комментариев
    """
    connection = db_crm.get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                c.CommentID,
                c.CommentText,
                c.CommentDate,
                CONCAT(e.FirstName, ' ', e.LastName) as EmployeeName
            FROM ObjectiveComments c
            LEFT JOIN ListEmployee e ON c.EmployeeID = e.EmployeeID
            WHERE c.ObjectiveID = %s
            ORDER BY c.CommentDate DESC
        """, (objective_id,))

        return cursor.fetchall()

    except Error as e:
        print(f"Ошибка получения комментариев: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def add_objective_comment(objective_id: int, employee_id: int, comment_text: str) -> bool:
    """
    Добавляет комментарий к задаче

    Args:
        objective_id: ID задачи
        employee_id: ID сотрудника
        comment_text: Текст комментария

    Returns:
        True если успешно
    """
    connection = db_crm.get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO ObjectiveComments (ObjectiveID, EmployeeID, CommentText)
            VALUES (%s, %s, %s)
        """, (objective_id, employee_id, comment_text))

        connection.commit()
        return True

    except Error as e:
        print(f"Ошибка добавления комментария: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()