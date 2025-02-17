import json
import urllib

import mock
from flask import jsonify


def test_run_report_json_parameters(flask_app, setup_workspace):
    with flask_app.test_client() as client:
        report_name = "fake/report"
        overrides = {"a": 1}
        report_title = "title"
        mailto = "abc@email.asdkj"
        mailfrom = "test@example.com"
        generate_pdf = True
        hide_code = True
        scheduler_job_id = "abc/123"
        payload = {
            "overrides": json.dumps(overrides),
            "report_title": report_title,
            "mailto": mailto,
            "generate_pdf": generate_pdf,
            "hide_code": hide_code,
            "scheduler_job_id": scheduler_job_id,
            "mailfrom": mailfrom,
        }
        with mock.patch("notebooker.web.routes.run_report.run_report") as rr:
            rr.return_value = "fake_job_id"
            rv = client.post(
                f"/run_report_json/{report_name}?{urllib.parse.urlencode(payload)}"
            )
            assert rv.data == jsonify({"id": "fake_job_id"}).data
            assert rv.status_code == 202, rv.data
            rr.assert_called_with(
                report_name,
                report_title,
                mailto,
                overrides,
                generate_pdf_output=generate_pdf,
                hide_code=hide_code,
                scheduler_job_id=scheduler_job_id,
                mailfrom=mailfrom,
            )
