wrk.method = "PUT"
wrk.headers["Content-Type"] = "application/json"
wrk.headers["accept"] = "application/json"

request = function()
  local id = math.random(100000)
  local body = string.format('{"key":"stress-%d","value":"val-%d"}', id, id)
  return wrk.format(nil, "/store", nil, body)
end