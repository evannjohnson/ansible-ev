package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/google/jsonschema-go/jsonschema"
)

func main() {
	if len(os.Args) < 3 {
		fmt.Fprintf(os.Stderr, "Usage: validate-presets <schema.json> <preset.json> [preset.json ...]\n")
		os.Exit(1)
	}

	schemaPath := os.Args[1]
	presetPaths := os.Args[2:]

	// Load and parse the schema.
	schemaData, err := os.ReadFile(schemaPath)
	if err != nil {
		log.Fatalf("reading schema %q: %v", schemaPath, err)
	}

	var schema jsonschema.Schema
	if err := json.Unmarshal(schemaData, &schema); err != nil {
		log.Fatalf("parsing schema %q: %v", schemaPath, err)
	}

	resolved, err := schema.Resolve(nil)
	if err != nil {
		log.Fatalf("resolving schema: %v", err)
	}

	// Validate each preset file.
	failed := 0
	for _, path := range presetPaths {
		data, err := os.ReadFile(path)
		if err != nil {
			fmt.Printf("FAIL  %s: %v\n", path, err)
			failed++
			continue
		}

		var instance any
		if err := json.Unmarshal(data, &instance); err != nil {
			fmt.Printf("FAIL  %s: %v\n", path, err)
			failed++
			continue
		}

		if err := resolved.Validate(instance); err != nil {
			fmt.Printf("FAIL  %s: %v\n", path, err)
			failed++
		} else {
			fmt.Printf("OK    %s\n", path)
		}
	}

	if failed > 0 {
		os.Exit(1)
	}
}
