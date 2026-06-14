from decimal import Decimal

from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.seat import Seat


class SeatRepository:
    session: AsyncSession
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_event_seats(self, id_event: int, count_rows: int, count_cols: int, base_price: Decimal):
        seats = []
        for i_row in range(1, count_rows + 1):
            for i_col in range(1, count_cols + 1):
                seat = Seat(row_number=i_row, seat_number=i_col, price=base_price, id_event=id_event)
                seats.append(seat)

        self.session.add_all(seats)
        await self.session.commit()

    async def get_seats_by_event(self, id_event: int) -> Sequence[Seat]:
        result = await self.session.execute(select(Seat).where(Seat.id_event == id_event))
        seats = result.scalars().all()

        return seats




