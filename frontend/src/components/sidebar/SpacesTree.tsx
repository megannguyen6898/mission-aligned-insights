import React from "react";
import {
  Building2,
  ChevronDown,
  ChevronRight,
  FileSpreadsheet,
  FolderKanban,
  Sparkles,
  Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

export type SpaceType = "organization" | "program" | "project" | "dataset";
export type SpaceStatus = "ready" | "processing" | "action_needed";

export interface SpaceNode {
  id: string;
  name: string;
  type: SpaceType;
  description?: string;
  lastUpdated?: string;
  beneficiariesServed?: string;
  sdgFocus?: string;
  status?: SpaceStatus;
  metrics?: Array<{ label: string; value: string }>;
  children?: SpaceNode[];
}

const statusStyles: Record<SpaceStatus, string> = {
  ready: "bg-emerald-500/15 text-emerald-600 border border-emerald-500/20",
  processing: "bg-amber-500/15 text-amber-600 border border-amber-500/20",
  action_needed: "bg-rose-500/15 text-rose-600 border border-rose-500/20",
};

const typeIconMap: Record<SpaceType, React.ReactNode> = {
  organization: <Building2 className="h-4 w-4" />,
  program: <Users className="h-4 w-4" />,
  project: <FolderKanban className="h-4 w-4" />,
  dataset: <FileSpreadsheet className="h-4 w-4" />,
};

const defaultSpaces: SpaceNode[] = [
  {
    id: "org-impact-collective",
    name: "Impact Collective",
    type: "organization",
    description: "Global youth development org",
    lastUpdated: "Updated 2 days ago",
    sdgFocus: "SDG 4 • SDG 8",
    children: [
      {
        id: "program-youth-skills",
        name: "Youth Skills Initiative",
        type: "program",
        beneficiariesServed: "1,240 youth",
        lastUpdated: "Impact metrics refreshed weekly",
        sdgFocus: "SDG 4",
        children: [
          {
            id: "project-bootcamps",
            name: "Bootcamp Cohort 2024",
            type: "project",
            metrics: [
              { label: "Graduation rate", value: "92%" },
              { label: "AI confidence", value: "High" },
            ],
            children: [
              {
                id: "dataset-outcomes-q2",
                name: "Q2 2024 Outcomes.xlsx",
                type: "dataset",
                status: "ready",
                lastUpdated: "Validated 4 days ago",
              },
              {
                id: "dataset-survey",
                name: "Youth survey responses.csv",
                type: "dataset",
                status: "processing",
                lastUpdated: "AI mapping in progress",
              },
            ],
          },
        ],
      },
      {
        id: "program-entrepreneurship",
        name: "Community Entrepreneurship",
        type: "program",
        beneficiariesServed: "320 founders",
        lastUpdated: "Updated 5 days ago",
        sdgFocus: "SDG 8",
        children: [
          {
            id: "project-microfinance",
            name: "Microfinance Pilot",
            type: "project",
            metrics: [
              { label: "Capital deployed", value: "$450K" },
              { label: "Communities", value: "12" },
            ],
            children: [
              {
                id: "dataset-loan-ledger",
                name: "Loan ledger.xlsx",
                type: "dataset",
                status: "action_needed",
                lastUpdated: "Missing poverty depth metrics",
              },
            ],
          },
        ],
      },
    ],
  },
];

interface SpacesTreeProps {
  collapsed?: boolean;
  spaces?: SpaceNode[];
  onSelectNode?: (node: SpaceNode) => void;
}

interface TreeNodeProps {
  node: SpaceNode;
  depth: number;
  expanded: Record<string, boolean>;
  onToggle: (id: string) => void;
  collapsed?: boolean;
  onSelectNode?: (node: SpaceNode) => void;
}

const TreeNode: React.FC<TreeNodeProps> = ({
  node,
  depth,
  expanded,
  onToggle,
  collapsed,
  onSelectNode,
}) => {
  const hasChildren = !!node.children?.length;
  const isExpanded = expanded[node.id] ?? depth === 0;
  const content = (
    <button
      type="button"
      onClick={() => {
        if (hasChildren) {
          onToggle(node.id);
        } else {
          onSelectNode?.(node);
        }
      }}
      className={cn(
        "group flex w-full items-start gap-3 rounded-xl border border-transparent bg-muted/40 pr-3 py-3 text-left transition hover:bg-muted",
        hasChildren && "hover:border-border",
        !hasChildren && "hover:border-primary/40",
      )}
      aria-expanded={hasChildren ? isExpanded : undefined}
      style={collapsed ? undefined : { paddingLeft: 12 + Math.min(depth, 4) * 12 }}
    >
      <div className="flex items-center gap-2 text-muted-foreground">
        {hasChildren ? (
          isExpanded ? (
            <ChevronDown className="h-4 w-4" aria-hidden />
          ) : (
            <ChevronRight className="h-4 w-4" aria-hidden />
          )
        ) : (
          <Sparkles className="h-4 w-4 text-primary" aria-hidden />
        )}
        <span className="text-muted-foreground">{typeIconMap[node.type]}</span>
      </div>
      <div className="flex-1 space-y-1">
        <p className="text-sm font-medium leading-5 text-foreground">
          {node.name}
        </p>
        {node.description && !collapsed && (
          <p className="text-xs text-muted-foreground">{node.description}</p>
        )}
        {!collapsed && node.metrics?.length && (
          <div className="flex flex-wrap gap-1.5">
            {node.metrics.map((metric) => (
              <Badge
                key={`${node.id}-${metric.label}`}
                variant="secondary"
                className="bg-primary/10 text-primary border border-primary/20"
              >
                {metric.label}: {metric.value}
              </Badge>
            ))}
          </div>
        )}
        {!collapsed && node.lastUpdated && (
          <p className="text-xs text-muted-foreground/80">{node.lastUpdated}</p>
        )}
        {!collapsed && node.beneficiariesServed && (
          <p className="text-xs text-muted-foreground/80">
            {node.beneficiariesServed}
          </p>
        )}
        {!collapsed && node.sdgFocus && (
          <p className="text-xs text-muted-foreground/80">{node.sdgFocus}</p>
        )}
      </div>
      {!collapsed && node.status && (
        <Badge className={cn("capitalize", statusStyles[node.status])}>
          {node.status === "action_needed" ? "Action needed" : node.status}
        </Badge>
      )}
    </button>
  );

  return (
    <div className="space-y-2">
      {collapsed ? (
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              type="button"
              size="icon"
              variant="ghost"
              className="h-10 w-10 rounded-xl border border-border/60 bg-muted/40"
              onClick={() => {
                if (hasChildren) {
                  onToggle(node.id);
                } else {
                  onSelectNode?.(node);
                }
              }}
            >
              {typeIconMap[node.type]}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right" className="max-w-xs text-left">
            <p className="text-sm font-medium text-foreground">{node.name}</p>
            {node.lastUpdated && (
              <p className="text-xs text-muted-foreground">{node.lastUpdated}</p>
            )}
          </TooltipContent>
        </Tooltip>
      ) : (
        content
      )}
      {hasChildren && isExpanded && (
        <div className={cn("space-y-2", collapsed ? "hidden" : "")}
          role="group"
          aria-label={`${node.name} subspaces`}
        >
          {node.children!.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              depth={depth + 1}
              expanded={expanded}
              onToggle={onToggle}
              collapsed={collapsed}
              onSelectNode={onSelectNode}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const SpacesTree: React.FC<SpacesTreeProps> = ({
  collapsed = false,
  spaces = defaultSpaces,
  onSelectNode,
}) => {
  const [expanded, setExpanded] = React.useState<Record<string, boolean>>(() => {
    const defaults: Record<string, boolean> = {};
    spaces.forEach((space) => {
      defaults[space.id] = true;
      space.children?.forEach((child) => {
        defaults[child.id] = child.type !== "dataset";
      });
    });
    return defaults;
  });

  const handleToggle = React.useCallback((id: string) => {
    setExpanded((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  }, []);

  return (
    <TooltipProvider delayDuration={100}>
      <div
        className={cn("space-y-3", collapsed ? "items-center" : "")}
        aria-label="Spaces navigation"
      >
        {!collapsed && (
          <div className="px-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Spaces
            </p>
            <p className="text-xs text-muted-foreground/80">
              Navigate programs, projects, and datasets
            </p>
          </div>
        )}
        <div
          className={cn("space-y-2", collapsed ? "flex flex-col items-center gap-2" : "px-1")}
          role="tree"
        >
          {spaces.map((space) => (
            <TreeNode
              key={space.id}
              node={space}
              depth={0}
              expanded={expanded}
              onToggle={handleToggle}
              collapsed={collapsed}
              onSelectNode={onSelectNode}
            />
          ))}
        </div>
      </div>
    </TooltipProvider>
  );
};
