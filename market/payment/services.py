import random
import uuid
from dataclasses import asdict, dataclass

TEMP_PAYMENTS_STOR = dict()

MESSAGES = (
    "Код 04 — изъять карту без указания причины",
    "Код 05 – отказать без указания причины",
    "Код 17 – отказать, отклонено пользователем карты",
    "Код 19 — тех ошибка на стороне банка",
    "Код 41 – изъять, утерянная карта",
    "Код 43 – изъять, украденная карта",
    "Код 51 – отказать, на счете недостаточно средств",
    "Код 55 – отказать, неверно введенный ПИН-код"
)


def get_random_error_message() -> str:
    """
    Возвращает рандомную строку сообщающую об ошибке оплаты
    """
    return random.choice(MESSAGES)


@dataclass
class PaymentStatus:
    payment_uid: uuid
    card_number: str
    order_id: int = None
    error_message: str = ""
    status: str = "FAIL"


class PaymentsList:
    def __init__(self):
        self.stor = TEMP_PAYMENTS_STOR

    def get(self, payment_uid):
        status = self.stor.get(payment_uid, None)
        if status is None:
            status = {
                "payment_uid": payment_uid,
                "error_message": f"Номер операции {payment_uid} не зарегистрирован в системе"
            }
        return status

    def set(self, obj: PaymentStatus):
        if obj.payment_uid in self.stor:
            return
        self.stor[obj.payment_uid] = self.__fake_status_calc(obj)

    def __fake_status_calc(self, obj):
        obj.status = "SUCCESS" if self.__check_sum_card(obj.card_number) else "FAIL"
        if obj.status == "FAIL":
            obj.error_message = get_random_error_message()
        return obj

    @staticmethod
    def __check_sum_card(card_number):
        if int(card_number[-1]) % 2 == 0 and card_number[-1] != '0':
            return True
        return False


class PaymentProcessing:
    def __init__(self, card_number: str = None, order_id: int = None):
        self.payment_uid = None
        self.order_id = order_id
        self.card_number = card_number
        self.payments = PaymentsList()

    def __create_status_obj(self):
        if self.payment_uid is None:
            self.payment_uid = uuid.uuid4()
        status = PaymentStatus(
            payment_uid=self.payment_uid,
            card_number=self.card_number,
            order_id=self.order_id)
        self.payments.set(status)

    def processing(self):
        """
        Отправить данные в платежную систему
        """
        self.__create_status_obj()

    def get_status(self, payment_uid):
        """
        Получить статус платежа по уникальному номеру операции
        """
        status = self.payments.get(payment_uid)
        self.__save_payed_status_to_db(status)
        return asdict(status)

    def __save_payed_status_to_db(self, obj: PaymentStatus):
        """
        Сохранение статуса оплаты и сообщения об ошибке в базу данных модель Order
        """
        ...
