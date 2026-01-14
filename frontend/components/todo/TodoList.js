"use client";
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = TodoList;
var react_1 = require("react");
var todo_service_1 = require("@/services/todo.service");
var TodoItem_1 = require("./TodoItem");
var UpdateTodoModal_1 = require("./UpdateTodoModal");
var api_1 = require("@/services/api");
var navigation_1 = require("next/navigation");
function TodoList() {
    var _this = this;
    var _a = (0, react_1.useState)(null), data = _a[0], setData = _a[1];
    var _b = (0, react_1.useState)(true), isLoading = _b[0], setIsLoading = _b[1];
    var _c = (0, react_1.useState)(null), error = _c[0], setError = _c[1];
    var _d = (0, react_1.useState)(1), page = _d[0], setPage = _d[1];
    var _e = (0, react_1.useState)(null), editingTodo = _e[0], setEditingTodo = _e[1];
    var router = (0, navigation_1.useRouter)();
    var fetchTodos = (0, react_1.useCallback)(function () { return __awaiter(_this, void 0, void 0, function () {
        var response, err_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    setIsLoading(true);
                    setError(null);
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 3, 4, 5]);
                    return [4 /*yield*/, (0, todo_service_1.getTodos)(page)];
                case 2:
                    response = _a.sent();
                    setData(response);
                    return [3 /*break*/, 5];
                case 3:
                    err_1 = _a.sent();
                    if ((0, api_1.isAuthError)(err_1)) {
                        router.push("/signin");
                        return [2 /*return*/];
                    }
                    setError("Failed to load todos. Please try again.");
                    console.error("Failed to fetch todos:", err_1);
                    return [3 /*break*/, 5];
                case 4:
                    setIsLoading(false);
                    return [7 /*endfinally*/];
                case 5: return [2 /*return*/];
            }
        });
    }); }, [page, router]);
    (0, react_1.useEffect)(function () {
        fetchTodos();
    }, [fetchTodos]);
    var handleUpdate = function () {
        fetchTodos();
    };
    var handleEdit = function (todo) {
        setEditingTodo(todo);
    };
    var totalPages = data ? Math.ceil(data.total / 20) : 0;
    if (isLoading && !data) {
        return (<div className="space-y-4">
        {[1, 2, 3].map(function (i) { return (<div key={i} className="card animate-pulse">
            <div className="flex items-start gap-4">
              <div className="h-5 w-5 bg-gray-200 rounded"/>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"/>
                <div className="h-3 bg-gray-200 rounded w-1/2"/>
              </div>
            </div>
          </div>); })}
      </div>);
    }
    if (error) {
        return (<div className="card text-center py-8">
        <p className="text-red-600 mb-4">{error}</p>
        <button onClick={fetchTodos} className="btn-primary">
          Try Again
        </button>
      </div>);
    }
    if (!data || data.todos.length === 0) {
        return (<div className="card text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No todos yet</h3>
        <p className="text-gray-500">
          Add your first todo using the form above!
        </p>
      </div>);
    }
    return (<>
      <div className="space-y-4">
        {data.todos.map(function (todo) { return (<TodoItem_1.default key={todo.id} todo={todo} onUpdate={handleUpdate} onEdit={handleEdit}/>); })}
      </div>

      {totalPages > 1 && (<div className="flex justify-center items-center gap-4 mt-6">
          <button onClick={function () { return setPage(function (p) { return Math.max(1, p - 1); }); }} disabled={page === 1 || isLoading} className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed">
            Previous
          </button>
          <span className="text-gray-600">
            Page {page} of {totalPages}
          </span>
          <button onClick={function () { return setPage(function (p) { return Math.min(totalPages, p + 1); }); }} disabled={page === totalPages || isLoading} className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed">
            Next
          </button>
        </div>)}

      {editingTodo && (<UpdateTodoModal_1.default todo={editingTodo} onClose={function () { return setEditingTodo(null); }} onSuccess={function () {
                setEditingTodo(null);
                handleUpdate();
            }}/>)}
    </>);
}
