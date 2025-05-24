namespace Demo.GenerateCode.Domain.Entity
{
    /// <summary>
    /// DTO para la entidad People
    /// </summary>
    public class People
    {
        /// <summary>
        /// Identificador único
        /// </summary>
        public int Id { get; set; }

        /// <summary>
        /// Nombre completo
        /// </summary>
        public string Name { get; set; }

        /// <summary>
        /// Fecha de nacimiento
        /// </summary>
        public DateTime BirthOfDate { get; set; }
    }
}