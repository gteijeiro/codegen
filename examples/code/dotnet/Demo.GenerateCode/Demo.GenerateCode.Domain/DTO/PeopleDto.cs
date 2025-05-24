namespace Demo.GenerateCode.Domain.DTO
{
    public class PeopleDto
    { 
        /// <summary>
        /// Identificador único de la persona
        /// </summary>
        public int Id { get; set; }
        
        /// <summary>
        /// Nombre completo de la persona
        /// </summary>
        public string Name { get; set; }
        
        /// <summary>
        /// Fecha de nacimiento de la persona
        /// </summary>
        public DateTime BirthOfDate { get; set; }
        
        /// <summary>
        /// Edad calculada de la persona
        /// </summary>
        public int Age { get; set; }
    }
}