/* address: 0x0050f680 */
/* name: CSpawnerThng__IsSpawnTypeAllowed */
/* signature: int __cdecl CSpawnerThng__IsSpawnTypeAllowed(int spawn_type) */


int __cdecl CSpawnerThng__IsSpawnTypeAllowed(int spawn_type)

{
  switch(spawn_type) {
  case 4:
  case 5:
  case 6:
  case 7:
  case 8:
  case 9:
  case 10:
  case 0xb:
  case 0xc:
  case 0xd:
  case 0xe:
  case 0xf:
  case 0x10:
  case 0x11:
  case 0x12:
  case 0x13:
  case 0x14:
  case 0x16:
  case 0x17:
  case 0x18:
    return 0;
  default:
    return 1;
  }
}
