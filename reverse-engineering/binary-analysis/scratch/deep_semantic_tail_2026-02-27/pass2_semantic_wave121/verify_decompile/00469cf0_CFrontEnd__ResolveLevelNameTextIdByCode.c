/* address: 0x00469cf0 */
/* name: CFrontEnd__ResolveLevelNameTextIdByCode */
/* signature: int __cdecl CFrontEnd__ResolveLevelNameTextIdByCode(int param_1) */


int __cdecl CFrontEnd__ResolveLevelNameTextIdByCode(int param_1)

{
  if (param_1 < 0x1b0) {
    if (param_1 == 0x1af) {
      return 0x161e029;
    }
    if (param_1 < 0x138) {
      if (param_1 == 0x137) {
        return 0x160f8cd;
      }
      switch(param_1) {
      case 100:
        return 0x15f8838;
      case 0x6e:
        return 0x15fe3a7;
      case 200:
      case 0xc9:
        return 0x15fb8ab;
      case 0xd3:
        return 0x160c857;
      case 0xd4:
        return 0x1617c93;
      case 0xdd:
        return 0x16123c8;
      case 0xde:
        return 0x161d805;
      case 0xe7:
        return 0x1617f39;
      case 0xe8:
        return 0x1623377;
      case 300:
        return 0x15fe91e;
      }
    }
    else {
      switch(param_1) {
      case 0x138:
        return 0x161ad0b;
      case 0x141:
        return 0x161543f;
      case 0x142:
        return 0x162087e;
      case 0x14b:
        return 0x161afb1;
      case 0x14c:
        return 0x16263f1;
      case 400:
        return 0x1601991;
      case 0x19b:
        return 0x1612943;
      case 0x19c:
        return 0x161dd83;
      case 0x1a5:
        return 0x16184b6;
      case 0x1a6:
        return 0x16238f7;
      }
    }
  }
  else if (param_1 < 0x265) {
    if (param_1 == 0x264) {
      return 0x1623e73;
    }
    switch(param_1) {
    case 0x1b0:
      return 0x162946b;
    case 500:
      return 0x1604a04;
    case 0x1ff:
      return 0x16159b9;
    case 0x200:
      return 0x1620dfb;
    case 0x209:
      return 0x161b52d;
    case 0x20a:
      return 0x1626970;
    case 0x20b:
      return 0x1631db3;
    case 0x20c:
      return 0x163d1f6;
    case 600:
      return 0x1607a77;
    case 0x263:
      return 0x1618a2f;
    }
  }
  else {
    switch(param_1) {
    case 0x26d:
      return 0x161e5a4;
    case 0x26e:
      return 0x16299e9;
    case 700:
      return 0x160aaea;
    case 0x2c6:
      return 0x161065f;
    case 0x2d0:
      return 0x16161d4;
    case 0x2db:
      return 0x1627191;
    case 0x2dc:
      return 0x16325d9;
    case 0x2e5:
      return 0x162cd07;
    case 0x2e6:
      return 0x1638150;
    case 800:
      return 0x160db5d;
    }
  }
  return -1;
}
