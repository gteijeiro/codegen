using Demo.GenerateCode.Api.Extensions;
using Demo.GenerateCode.Insfrastructure.Context;
using Demo.GenerateCode.Service.Mapper;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// Read connection string from appsettings.json

DemoCollectionExtensions.AddDatabase(builder.Services, builder.Configuration);
DemoCollectionExtensions.AddServices(builder.Services);
builder.Services.AddAutoMapper(typeof(MappingProfile));

builder.Services.AddControllers();
// Add Swagger services
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<DemoDbContext>();
    db.Database.EnsureCreated();
    db.Database.Migrate();
}

// Configure the HTTP request pipeline.

builder.Services.AddCors();
// Enable Swagger middleware
app.UseSwagger();
app.UseSwaggerUI();

app.UseHttpsRedirection();

// Add this line before app.UseHttpsRedirection() to enable routing and authorization if needed
app.UseRouting();
app.MapControllers();

app.Run();

