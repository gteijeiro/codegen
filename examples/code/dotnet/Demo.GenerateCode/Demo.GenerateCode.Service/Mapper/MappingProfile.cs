using AutoMapper;
using Demo.GenerateCode.Domain.DTO;
using Demo.GenerateCode.Domain.Entity;

namespace Demo.GenerateCode.Service.Mapper
{
    public class MappingProfile : Profile
    {
        public MappingProfile()
        {
            CreateMap<PeopleDto, People>();
            CreateMap<People, PeopleDto>();
        }
    }

}
