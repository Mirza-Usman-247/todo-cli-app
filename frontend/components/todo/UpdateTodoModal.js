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
exports.default = UpdateTodoModal;
var react_1 = require("react");
var todo_service_1 = require("@/services/todo.service");
var api_1 = require("@/services/api");
function UpdateTodoModal(_a) {
    var _this = this;
    var todo = _a.todo, onClose = _a.onClose, onSuccess = _a.onSuccess;
    var _b = (0, react_1.useState)(todo.title), title = _b[0], setTitle = _b[1];
    var _c = (0, react_1.useState)(todo.description || ""), description = _c[0], setDescription = _c[1];
    var _d = (0, react_1.useState)(false), isLoading = _d[0], setIsLoading = _d[1];
    var _e = (0, react_1.useState)(null), error = _e[0], setError = _e[1];
    (0, react_1.useEffect)(function () {
        setTitle(todo.title);
        setDescription(todo.description || "");
    }, [todo]);
    var handleSubmit = function (e) { return __awaiter(_this, void 0, void 0, function () {
        var updates, newDescription, err_1, message;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    e.preventDefault();
                    setError(null);
                    if (!title.trim()) {
                        setError("Title is required");
                        return [2 /*return*/];
                    }
                    if (title.length > 255) {
                        setError("Title must be 255 characters or less");
                        return [2 /*return*/];
                    }
                    if (description && description.length > 1000) {
                        setError("Description must be 1000 characters or less");
                        return [2 /*return*/];
                    }
                    updates = {};
                    if (title.trim() !== todo.title) {
                        updates.title = title.trim();
                    }
                    newDescription = description.trim() || undefined;
                    if (newDescription !== (todo.description || undefined)) {
                        updates.description = newDescription;
                    }
                    if (Object.keys(updates).length === 0) {
                        onClose();
                        return [2 /*return*/];
                    }
                    setIsLoading(true);
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 3, 4, 5]);
                    return [4 /*yield*/, (0, todo_service_1.updateTodo)(todo.id, updates)];
                case 2:
                    _a.sent();
                    onSuccess();
                    return [3 /*break*/, 5];
                case 3:
                    err_1 = _a.sent();
                    message = err_1 instanceof api_1.ApiException ? err_1.detail : "Failed to update todo";
                    setError(message);
                    return [3 /*break*/, 5];
                case 4:
                    setIsLoading(false);
                    return [7 /*endfinally*/];
                case 5: return [2 /*return*/];
            }
        });
    }); };
    var handleBackdropClick = function (e) {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };
    return (<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={handleBackdropClick}>
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Edit Todo</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600" disabled={isLoading}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4">
          {error && (<div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
              {error}
            </div>)}

          <div className="mb-4">
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
              Title
            </label>
            <input id="title" type="text" value={title} onChange={function (e) { return setTitle(e.target.value); }} className="input-field" disabled={isLoading} maxLength={255} autoFocus/>
          </div>

          <div className="mb-4">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description (optional)
            </label>
            <textarea id="description" value={description} onChange={function (e) { return setDescription(e.target.value); }} className="input-field resize-none" rows={4} disabled={isLoading} maxLength={1000}/>
            <div className="mt-1 text-xs text-gray-400">
              {description.length}/1000 characters
            </div>
          </div>

          <div className="flex gap-3 justify-end">
            <button type="button" onClick={onClose} disabled={isLoading} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={isLoading || !title.trim()} className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed">
              {isLoading ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>);
}
