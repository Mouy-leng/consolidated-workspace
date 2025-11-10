import { z } from "zod";

// Resource schema
export const resourceSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string(),
  skillLevel: z.enum(["beginner", "intermediate", "advanced"]),
  category: z.enum(["programming", "design", "marketing", "data-science"]),
  resourceType: z.enum(["video", "article", "course", "tutorial"]),
  duration: z.string(),
  imageUrl: z.string(),
  featured: z.boolean().default(false),
  createdAt: z.date().default(() => new Date()),
});

export type Resource = z.infer<typeof resourceSchema>;

// Insert schema (for creating new resources)
export const insertResourceSchema = resourceSchema.omit({
  id: true,
  createdAt: true,
});

export type InsertResource = z.infer<typeof insertResourceSchema>;

// Query filters schema
export const resourceFiltersSchema = z.object({
  search: z.string().optional(),
  skillLevel: z.enum(["beginner", "intermediate", "advanced"]).optional(),
  category: z.enum(["programming", "design", "marketing", "data-science"]).optional(),
  resourceType: z.enum(["video", "article", "course", "tutorial"]).optional(),
  page: z.number().int().positive().default(1),
  limit: z.number().int().positive().max(50).default(12),
});

export type ResourceFilters = z.infer<typeof resourceFiltersSchema>;

// Response schema for paginated resources
export const resourcesResponseSchema = z.object({
  resources: z.array(resourceSchema),
  totalCount: z.number(),
  totalPages: z.number(),
  currentPage: z.number(),
  hasNextPage: z.boolean(),
  hasPrevPage: z.boolean(),
});

export type ResourcesResponse = z.infer<typeof resourcesResponseSchema>;
