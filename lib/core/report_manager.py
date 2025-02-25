# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Author: Mauro Soria

import threading
from lib.reports import CSVReport, HTMLReport, JSONReport, MarkdownReport, PlainTextReport, SimpleReport, XMLReport


class Result(object):
    def __init__(self, path, status, response):
        self.path = path
        self.status = status
        self.response = response

    def get_content_length(self):
        try:
            content_length = int(self.response.headers["content-length"])
        except (KeyError, ValueError):
            content_length = len(self.response.body)
        return content_length


class Report(object):
    def __init__(self, host, port, protocol, base_path):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.base_path = base_path
        self.results = []
        self.completed = False

        if self.base_path.endswith("/"):
            self.base_path = self.base_path[:-1]

        if self.base_path.startswith("/"):
            self.base_path = self.base_path[1:]

    def add_result(self, path, status, response):
        result = Result(path, status, response)
        self.results.append(result)


class ReportManager(object):
    def __init__(self, save_format, output_file):
        self.format = save_format
        self.reports = []
        self.report_obj = None
        self.output = output_file
        self.lock = threading.Lock()

    def update_report(self, report):
        if report not in self.reports:
            self.reports.append(report)
        self.write_report()

    def write_report(self):
        if self.report_obj is None:
            if self.format == "simple":
                report = SimpleReport(self.output, self.reports)
            elif self.format == "json":
                report = JSONReport(self.output, self.reports)
            elif self.format == "xml":
                report = XMLReport(self.output, self.reports)
            elif self.format == "md":
                report = MarkdownReport(self.output, self.reports)
            elif self.format == "csv":
                report = CSVReport(self.output, self.reports)
            elif self.format == "html":
                report = HTMLReport(self.output, self.reports)
            else:
                report = PlainTextReport(self.output, self.reports)

            self.report_obj = report

        with self.lock:
            self.report_obj.save()

    def save(self):
        with self.lock:
            self.output.save()

    def close(self):
        self.output.close()
