using Demo.GenerateCode.Domain.DTO;

namespace Demo.GenerateCode.Domain.Interfaces.Services
{
    /// <summary>
    /// Service interface for managing People entities.
    /// </summary>
    public interface IPeopleService
    {
        /// <summary>
        /// Get all items of People table.
        /// </summary>
        /// <returns>A list of all People entities.</returns>
        Task<IList<PeopleDto>> GetAll();

        /// <summary>
        /// Get a single People entity by its identifier.
        /// </summary>
        /// <param name="id">The identifier of the People entity.</param>
        /// <returns>The People entity with the specified identifier.</returns>
        Task<PeopleDto> GetOne(int id);

        /// <summary>
        /// Update an existing People entity.
        /// </summary>
        /// <param name="entityInput">The People entity to update.</param>
        Task Update(PeopleDto entityInput);

        /// <summary>
        /// Add a new People entity.
        /// </summary>
        /// <param name="People">The People entity to add.</param>
        Task Add(PeopleDto entityInput);

        /// <summary>
        /// Delete a People entity by its identifier.
        /// </summary>
        /// <param name="id">The identifier of the People entity to delete.</param>
        Task Delete(int id);

        /// <summary>
        /// Gets the age of a person.
        /// </summary>
        /// <returns>The age as an integer.</returns>
        Task<PeopleDto> CalculateAge(int id);
    }
}