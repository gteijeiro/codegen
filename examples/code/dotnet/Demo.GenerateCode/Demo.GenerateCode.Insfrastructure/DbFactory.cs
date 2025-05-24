using Demo.GenerateCode.Insfrastructure.Context;
using Microsoft.EntityFrameworkCore;

namespace Demo.GenerateCode.Infrastructure
{
    public class DbFactory : IDisposable
    {
        private bool _disposed;
        private Func<DemoDbContext> _instanceFunc;
        private DbContext _dbContext;
        public DbContext DbContext => _dbContext ?? (_dbContext = _instanceFunc.Invoke());

        public DbFactory(Func<DemoDbContext> dbContextFactory)
        {
            _instanceFunc = dbContextFactory;
        }

        public void Dispose()
        {
            if (!_disposed && _dbContext != null)
            {
                _disposed = true;
                _dbContext.Dispose();
            }
        }
    }
}