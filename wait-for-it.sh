#!/usr/bin/env bash
host="$1"
shift
cmd="$@"

until nc -z $host; do
  >&2 echo "⏳ A aguardar $host..."
  sleep 1
done

>&2 echo "✅ $host disponível, a iniciar..."
exec $cmd
