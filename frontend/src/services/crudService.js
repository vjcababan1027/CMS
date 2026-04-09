import { api } from "./api";

function list(resource, params = {}) {
  return api.get(resource, { params }).then((r) => r.data);
}
function getOne(resource, id) {
  return api.get(`${resource}/${id}`).then((r) => r.data);
}
function create(resource, payload) {
  return api.post(resource, payload).then((r) => r.data);
}
function update(resource, id, payload) {
  return api.put(`${resource}/${id}`, payload).then((r) => r.data);
}
function remove(resource, id) {
  return api.delete(`${resource}/${id}`).then((r) => r.data);
}

export const usersService = {
  list: (params) => list("/users", params),
  getOne: (id) => getOne("/users", id),
  create: (payload) => create("/auth/register", payload),
  update: (id, payload) => update("/users", id, payload),
  remove: (id) => remove("/users", id)
};

export const studentsService = {
  list: (params) => list("/students", params),
  getOne: (id) => getOne("/students", id),
  create: (payload) => create("/students", payload),
  update: (id, payload) => update("/students", id, payload),
  remove: (id) => remove("/students", id)
};

export const classesService = {
  list: (params) => list("/classes", params),
  getOne: (id) => getOne("/classes", id),
  create: (payload) => create("/classes", payload),
  update: (id, payload) => update("/classes", id, payload),
  remove: (id) => remove("/classes", id)
};

export const attendanceService = {
  list: (params) => list("/attendance", params),
  getOne: (id) => getOne("/attendance", id),
  create: (payload) => create("/attendance", payload),
  update: (id, payload) => update("/attendance", id, payload),
  remove: (id) => remove("/attendance", id),
  bulk: (payload) => create("/attendance/bulk", payload)
};

export const gradesService = {
  list: (params) => list("/grades", params),
  getOne: (id) => getOne("/grades", id),
  create: (payload) => create("/grades", payload),
  update: (id, payload) => update("/grades", id, payload),
  remove: (id) => remove("/grades", id),
  calculatePost: ({ student_id, class_id, period }) =>
    api
      .post("/grades/calculate", null, { params: { student_id, class_id, period } })
      .then((r) => r.data),
  calculatePath: ({ student_id, class_id, period }) =>
    api.get(`/grades/calculate/${student_id}/${class_id}/${period}`).then((r) => r.data),
  byStudentClass: (studentId, classId) =>
    api.get(`/grades/student/${studentId}/class/${classId}`).then((r) => r.data)
};

export const gradeWeightsService = {
  list: (params) => list("/grade-weights", params),
  getOne: (id) => getOne("/grade-weights", id),
  create: (payload) => create("/grade-weights", payload),
  update: (id, payload) => update("/grade-weights", id, payload),
  remove: (id) => remove("/grade-weights", id)
};

export const riskPredictionsService = {
  list: (params) => list("/risk-predictions", params),
  getOne: (id) => getOne("/risk-predictions", id),
  create: (payload) => create("/risk-predictions", payload),
  update: (id, payload) => update("/risk-predictions", id, payload),
  remove: (id) => remove("/risk-predictions", id)
};

export const parentReportingService = {
  list: () => list("/parent-reporting"),
  create: (payload) => create("/parent-reporting", payload),
  update: (id, payload) => update("/parent-reporting", id, payload),
  triggerBiweekly: () => api.post("/parent-reporting/trigger/biweekly").then((r) => r.data),
  triggerHighRisk: () => api.post("/parent-reporting/trigger/high-risk").then((r) => r.data)
};

export const reportsService = {
  studentClass: (studentId, classId) => api.get(`/reports/student/${studentId}/class/${classId}`).then((r) => r.data),
  classPerformance: (classId) => api.get(`/reports/class/${classId}/performance`).then((r) => r.data)
};

export const transmutationsService = {
  list: () => list("/grade-transmutations"),
  create: (payload) => create("/grade-transmutations", payload),
  update: (id, payload) => update("/grade-transmutations", id, payload),
  remove: (id) => remove("/grade-transmutations", id)
};

export const interventionsService = {
  byPrediction: (id) => api.get(`/interventions/risk-prediction/${id}`).then((r) => r.data),
  latestByStudentClass: (studentId, classId) =>
    api.get(`/interventions/student/${studentId}/class/${classId}/latest`).then((r) => r.data)
};
