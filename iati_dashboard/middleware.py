def cors_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        if request.path.startswith("/api/"):
            response["Access-Control-Allow-Origin"] = "*"
        return response

    return middleware
