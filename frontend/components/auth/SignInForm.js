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
exports.default = SignInForm;
var react_1 = require("react");
var link_1 = require("next/link");
var useAuth_1 = require("@/hooks/useAuth");
function SignInForm() {
    var _this = this;
    var _a = (0, react_1.useState)(""), email = _a[0], setEmail = _a[1];
    var _b = (0, react_1.useState)(""), password = _b[0], setPassword = _b[1];
    var _c = (0, useAuth_1.useSignIn)(), signIn = _c.signIn, isLoading = _c.isLoading, error = _c.error;
    var handleSubmit = function (e) { return __awaiter(_this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    e.preventDefault();
                    return [4 /*yield*/, signIn({ email: email, password: password })];
                case 1:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    }); };
    return (<form onSubmit={handleSubmit} className="space-y-4">
      {error && (<div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
          {error}
        </div>)}

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <input id="email" type="email" value={email} onChange={function (e) { return setEmail(e.target.value); }} required className="input-field" placeholder="you@example.com" disabled={isLoading}/>
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
          Password
        </label>
        <input id="password" type="password" value={password} onChange={function (e) { return setPassword(e.target.value); }} required className="input-field" placeholder="Enter your password" disabled={isLoading}/>
      </div>

      <button type="submit" disabled={isLoading} className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed">
        {isLoading ? "Signing in..." : "Sign In"}
      </button>

      <p className="text-center text-sm text-gray-600">
        Don&apos;t have an account?{" "}
        <link_1.default href="/signup" className="text-blue-600 hover:underline">
          Sign up
        </link_1.default>
      </p>
    </form>);
}
