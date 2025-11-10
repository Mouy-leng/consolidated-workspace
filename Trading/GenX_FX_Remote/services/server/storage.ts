import { Resource, InsertResource, ResourceFilters } from "@shared/schema";
import { nanoid } from "nanoid";

export interface IStorage {
  // Resource operations
  getResources(filters: ResourceFilters): Promise<{
    resources: Resource[];
    totalCount: number;
    totalPages: number;
    currentPage: number;
    hasNextPage: boolean;
    hasPrevPage: boolean;
  }>;
  getResourceById(id: string): Promise<Resource | null>;
  createResource(resource: InsertResource): Promise<Resource>;
  updateResource(id: string, resource: Partial<InsertResource>): Promise<Resource | null>;
  deleteResource(id: string): Promise<boolean>;
  getFeaturedResources(): Promise<Resource[]>;
}

export class MemStorage implements IStorage {
  private resources: Resource[] = [
    {
      id: "1",
      title: "JavaScript Fundamentals",
      description: "Learn the basics of JavaScript programming with hands-on examples and practical exercises.",
      skillLevel: "beginner",
      category: "programming",
      resourceType: "video",
      duration: "2h 30m",
      imageUrl: "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200",
      featured: true,
      createdAt: new Date(),
    },
    {
      id: "2",
      title: "UI/UX Design Principles",
      description: "Master the essential principles of user interface and experience design.",
      skillLevel: "intermediate",
      category: "design",
      resourceType: "article",
      duration: "15 min read",
      imageUrl: "https://images.unsplash.com/photo-1558655146-d09347e92766?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200",
      featured: true,
      createdAt: new Date(),
    },
    {
      id: "3",
      title: "Advanced Data Analysis",
      description: "Deep dive into statistical analysis and machine learning techniques.",
      skillLevel: "advanced",
      category: "data-science",
      resourceType: "course",
      duration: "8 weeks",
      imageUrl: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200",
      featured: true,
      createdAt: new Date(),
    },
    {
      id: "4",
      title: "Digital Marketing Strategies",
      description: "Learn effective digital marketing techniques to grow your online presence.",
      skillLevel: "beginner",
      category: "marketing",
      resourceType: "tutorial",
      duration: "45 min",
      imageUrl: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200",
      featured: true,
      createdAt: new Date(),
    },
    {
      id: "5",
      title: "Python Programming",
      description: "Advance your Python skills with object-oriented programming and data structures.",
      skillLevel: "intermediate",
      category: "programming",
      resourceType: "video",
      duration: "3h 15m",
      imageUrl: "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200",
      featured: true,
      createdAt: new Date(),
    },
    {
      id: "6",
      title: "Mobile App Design Mastery",
      description: "Create stunning mobile applications with advanced design patterns and user experience techniques.",
      skillLevel: "advanced",
      category: "design",
      resourceType: "course",
      duration: "6 weeks",
      imageUrl: "https://images.unsplash.com/photo-1512486130939-2c4f79935e4f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200",
      featured: true,
      createdAt: new Date(),
    },
  ];

  async getResources(filters: ResourceFilters) {
    let filteredResources = [...this.resources];

    // Apply search filter
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filteredResources = filteredResources.filter(
        resource =>
          resource.title.toLowerCase().includes(searchTerm) ||
          resource.description.toLowerCase().includes(searchTerm)
      );
    }

    // Apply skill level filter
    if (filters.skillLevel) {
      filteredResources = filteredResources.filter(
        resource => resource.skillLevel === filters.skillLevel
      );
    }

    // Apply category filter
    if (filters.category) {
      filteredResources = filteredResources.filter(
        resource => resource.category === filters.category
      );
    }

    // Apply resource type filter
    if (filters.resourceType) {
      filteredResources = filteredResources.filter(
        resource => resource.resourceType === filters.resourceType
      );
    }

    // Sort by created date (newest first)
    filteredResources.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());

    // Calculate pagination
    const totalCount = filteredResources.length;
    const totalPages = Math.ceil(totalCount / filters.limit);
    const currentPage = filters.page;
    const startIndex = (currentPage - 1) * filters.limit;
    const endIndex = startIndex + filters.limit;
    const paginatedResources = filteredResources.slice(startIndex, endIndex);

    return {
      resources: paginatedResources,
      totalCount,
      totalPages,
      currentPage,
      hasNextPage: currentPage < totalPages,
      hasPrevPage: currentPage > 1,
    };
  }

  async getResourceById(id: string): Promise<Resource | null> {
    return this.resources.find(resource => resource.id === id) || null;
  }

  async createResource(resource: InsertResource): Promise<Resource> {
    const newResource: Resource = {
      id: nanoid(),
      ...resource,
      createdAt: new Date(),
    };
    this.resources.push(newResource);
    return newResource;
  }

  async updateResource(id: string, updateData: Partial<InsertResource>): Promise<Resource | null> {
    const index = this.resources.findIndex(resource => resource.id === id);
    if (index === -1) return null;

    this.resources[index] = { ...this.resources[index], ...updateData };
    return this.resources[index];
  }

  async deleteResource(id: string): Promise<boolean> {
    const index = this.resources.findIndex(resource => resource.id === id);
    if (index === -1) return false;

    this.resources.splice(index, 1);
    return true;
  }

  async getFeaturedResources(): Promise<Resource[]> {
    return this.resources.filter(resource => resource.featured);
  }
}
