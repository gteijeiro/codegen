using Demo.GenerateCode.Domain.DTO;
using Demo.GenerateCode.Domain.Interfaces.Services;
using Microsoft.AspNetCore.Mvc;

namespace Demo.GenerateCode.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PeopleController : ControllerBase
    {
        private readonly IPeopleService _service;

        public PeopleController(IPeopleService service)
        {
            _service = service;
        }

        [HttpGet]
        public async Task<ActionResult<IList<PeopleDto>>> GetAll()
        {
            var result = await _service.GetAll();
            return Ok(result);
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<PeopleDto>> GetOne(int id)
        {
            var result = await _service.GetOne(id);
            if (result == null)
                return NotFound();
            return Ok(result);
        }

        [HttpPost]
        public async Task<IActionResult> Add([FromBody] PeopleDto dto)
        {
            await _service.Add(dto);
            return CreatedAtAction(nameof(GetOne), new { id = dto.Id }, dto);
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> Update(int id, [FromBody] PeopleDto dto)
        {
            if (id != dto.Id)
                return BadRequest();
            await _service.Update(dto);
            return NoContent();
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> Delete(int id)
        {
            await _service.Delete(id);
            return NoContent();
        }
    }
}
