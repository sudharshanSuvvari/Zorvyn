# app/utils/csv_export.py

import csv
import io
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any


def build_csv_response(
    data: List[Dict[str, Any]],
    filename: str = "export.csv"
) -> StreamingResponse:
    """
    Converts list of dicts into CSV streaming response
    """

    if not data:
        data = []

    def generate():
        buffer = io.StringIO()
        writer = None

        for row in data:
            if writer is None:
                writer = csv.DictWriter(buffer, fieldnames=row.keys())
                writer.writeheader()

            writer.writerow(row)
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

        buffer.close()

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )