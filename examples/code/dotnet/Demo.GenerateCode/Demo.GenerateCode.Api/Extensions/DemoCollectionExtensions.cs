using Demo.GenerateCode.Domain.Interfaces;
using Demo.GenerateCode.Domain.Interfaces.Services;
using Demo.GenerateCode.Infrastructure;
using Demo.GenerateCode.Insfrastructure.Context;
using Demo.GenerateCode.Service;
using Microsoft.EntityFrameworkCore;

namespace Demo.GenerateCode.Api.Extensions
{
    public static class DemoCollectionExtensions
    {
        /// <summary>
        /// Add needed instances for database
        /// </summary>
        /// <param name="services"></param>
        /// <param name="configuration"></param>
        /// <returns></returns>
        public static IServiceCollection AddDatabase(this IServiceCollection services, IConfiguration configuration)
        {
            var connectionString = configuration.GetConnectionString("DefaultConnection");

            // Configure DbContext with Scoped lifetime  
            services.AddDbContext<DemoDbContext>(options =>
            {
                options.UseSqlServer(connectionString,
                    sqlOptions => sqlOptions.CommandTimeout(120));
            }
            );

            services.AddScoped<Func<DemoDbContext>>((provider) => () => provider.GetService<DemoDbContext>());
            services.AddScoped<DbFactory>();
            services.AddScoped<IUnitOfWork, UnitOfWork>();

            return services;
        }

        /// <summary>
        /// Add instances of in-use services
        /// </summary>
        /// <param name="services"></param>
        /// <returns></returns>
        public static IServiceCollection AddServices(this IServiceCollection services)
        {
            return services.AddScoped<IPeopleService, PeopleService>();
        }
    }
}
