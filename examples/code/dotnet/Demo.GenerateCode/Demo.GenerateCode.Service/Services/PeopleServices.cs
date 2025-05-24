using AutoMapper;
using Demo.GenerateCode.Domain.DTO;
using Demo.GenerateCode.Domain.Entity;
using Demo.GenerateCode.Domain.Interfaces;
using Demo.GenerateCode.Domain.Interfaces.Services;

namespace Demo.GenerateCode.Service
{
    /// <summary>
    /// Servicio para manejar operaciones relacionadas con People
    /// </summary>
    public class PeopleService : IPeopleService
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly IMapper _mapper;

        /// <summary>
        /// Constructor del servicio
        /// </summary>
        public PeopleService(IUnitOfWork unitOfWork, IMapper mapper)
        {
            _unitOfWork = unitOfWork;
            _mapper = mapper;
        }

        /// <summary>
        /// Obtiene todos los registros de People
        /// </summary>
        public async Task<IList<PeopleDto>> GetAll()
        {
            var entityList = await _unitOfWork.Repository<People>().GetAllAsync();
            return _mapper.Map<IList<PeopleDto>>(entityList);
        }

        /// <summary>
        /// Obtiene un People por su ID
        /// </summary>
        public async Task<PeopleDto> GetOne(int id)
        {
            var entity = await _unitOfWork.Repository<People>().FindAsync(id);
            return _mapper.Map<PeopleDto>(entity);
        }

        /// <summary>
        /// Actualiza un registro de People
        /// </summary>
        public async Task Update(PeopleDto entityInput)
        {
            try
            {
                await _unitOfWork.BeginTransaction();

                var entityRepo = _unitOfWork.Repository<People>();
                var entity = await entityRepo.FindAsync(entityInput.Id);
                if (entity == null)
                    throw new KeyNotFoundException();

                _mapper.Map(entityInput, entity);

                await _unitOfWork.CommitTransaction();
            }
            catch (Exception)
            {
                await _unitOfWork.RollbackTransaction();
                throw;
            }
        }

        /// <summary>
        /// Agrega un nuevo registro de People
        /// </summary>
        public async Task Add(PeopleDto entityInput)
        {
            try
            {
                await _unitOfWork.BeginTransaction();

                var entityRepo = _unitOfWork.Repository<People>();
                var entity = _mapper.Map<People>(entityInput);
                await entityRepo.InsertAsync(entity);

                await _unitOfWork.CommitTransaction();
            }
            catch (Exception)
            {
                await _unitOfWork.RollbackTransaction();
                throw;
            }
        }

        /// <summary>
        /// Elimina un registro de People
        /// </summary>
        public async Task Delete(int id)
        {
            try
            {
                await _unitOfWork.BeginTransaction();

                var entityRepo = _unitOfWork.Repository<People>();
                var entity = await entityRepo.FindAsync(id);
                if (entity == null)
                    throw new KeyNotFoundException();

                await entityRepo.DeleteAsync(entity);

                await _unitOfWork.CommitTransaction();
            }
            catch (Exception)
            {
                await _unitOfWork.RollbackTransaction();
                throw;
            }
        }

        /// <summary>
        /// Calcula la edad basada en BirthOfDate y retorna el objeto con la edad actualizada
        /// </summary>
        public async Task<PeopleDto> CalculateAge(int id)
        {
            var entity = await _unitOfWork.Repository<People>().FindAsync(id);
            if (entity == null)
                throw new KeyNotFoundException();

            var dto = _mapper.Map<PeopleDto>(entity);
            dto.Age = CalculateAgeFromBirthDate(entity.BirthOfDate);
            return dto;
        }

        /// <summary>
        /// Método privado para calcular la edad a partir de una fecha de nacimiento
        /// </summary>
        private int CalculateAgeFromBirthDate(DateTime birthDate)
        {
            var today = DateTime.Today;
            var age = today.Year - birthDate.Year;
            if (birthDate.Date > today.AddYears(-age)) age--;
            return age;
        }
    }
}