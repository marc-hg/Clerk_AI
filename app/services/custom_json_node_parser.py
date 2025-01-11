
import json
from typing import List, Sequence, Any

from llama_index.core.node_parser import JSONNodeParser
from llama_index.core.schema import BaseNode


class CustomJSONNodeParser(JSONNodeParser):
    def _parse_nodes(
        self, nodes: Sequence[BaseNode], show_progress: bool = False, **kwargs: Any
    ) -> List[BaseNode]:
        all_nodes = []
        for node in nodes:
            try:
                # Load the JSON content
                data = json.loads(node.get_content(metadata_mode="NONE"))
                
                # Extract summary and metadata
                summary = data.get("summary", "")
                metadata = node.metadata

                # Create a node for the summary with metadata
                summary_node = BaseNode(
                    id_=self.id_func(),
                    text=summary,
                    metadata={
                        "source_file": metadata.get("source_file", ""),
                        "name": metadata.get("name", ""),
                        "email": metadata.get("email", ""),
                        "country": metadata.get("country", ""),
                        "skills": metadata.get("skills", []),
                        "summary": summary
                    }
                )
                all_nodes.append(summary_node)

            except json.JSONDecodeError:
                continue
        return all_nodes 