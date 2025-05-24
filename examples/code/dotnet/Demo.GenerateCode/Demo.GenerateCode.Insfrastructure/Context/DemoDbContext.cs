using Demo.GenerateCode.Domain.Entity;
using Microsoft.EntityFrameworkCore;

namespace Demo.GenerateCode.Insfrastructure.Context
{
    public class DemoDbContext : DbContext
    {
        public DemoDbContext(DbContextOptions options) : base(options)
        {
        }

        public DbSet<People> People { get; set; }
    }
}
