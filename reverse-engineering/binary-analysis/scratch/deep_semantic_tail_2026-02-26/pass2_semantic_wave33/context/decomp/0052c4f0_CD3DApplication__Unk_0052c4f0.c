/* address: 0x0052c4f0 */
/* name: CD3DApplication__Unk_0052c4f0 */
/* signature: int __stdcall CD3DApplication__Unk_0052c4f0(int param_1) */


int CD3DApplication__Unk_0052c4f0(int param_1)

{
  if (param_1 < -0x7dfffff7) {
    if (param_1 == -0x7dfffff8) {
      FatalError_LocalizedStringId('\0',0xbd,-1);
      return -0x7dfffff8;
    }
    if (param_1 < -0x7dfffffb) {
      if (param_1 == -0x7dfffffc) {
        FatalError_LocalizedStringId('\0',0xb9,-1);
        return -0x7dfffffc;
      }
      if (param_1 == -0x7ff8fff2) {
        FatalError_LocalizedStringId('\0',0xc2,-1);
        return -0x7ff8fff2;
      }
      if (param_1 == -0x7dffffff) {
        FatalError_LocalizedStringId('\0',0xb7,-1);
        return -0x7dffffff;
      }
      if (param_1 == -0x7dfffffd) {
        if (DAT_0088907c != '\0') {
          FatalError_LocalizedStringId('\0',0xb8,-1);
          return -0x7dfffffd;
        }
        FatalError_LocalizedStringId('\0',0xc5,-1);
        return -0x7dfffffd;
      }
    }
    else {
      if (param_1 == -0x7dfffffb) {
        FatalError_LocalizedStringId('\0',0xba,-1);
        return -0x7dfffffb;
      }
      if (param_1 == -0x7dfffffa) {
        FatalError_LocalizedStringId('\0',0xbb,-1);
        return -0x7dfffffa;
      }
      if (param_1 == -0x7dfffff9) {
        FatalError_LocalizedStringId('\0',0xbc,-1);
        return -0x7dfffff9;
      }
    }
  }
  else if (param_1 < -0x7789fe83) {
    if (param_1 == -0x7789fe84) {
      FatalError_LocalizedStringId('\0',0xc3,-1);
      return -0x7789fe84;
    }
    switch(param_1) {
    case -0x7dfffff7:
      FatalError_LocalizedStringId('\0',0xbe,-1);
      return param_1;
    case -0x7dfffff6:
      FatalError_LocalizedStringId('\0',0xc1,-1);
      return param_1;
    case -0x7dfffff5:
      FatalError_LocalizedStringId('\0',0xbf,-1);
      return param_1;
    case -0x7dfffff4:
      FatalError_LocalizedStringId('\0',0xc0,-1);
      return param_1;
    case -0x7dfffff3:
      FatalError_LocalizedStringId('\0',0xb6,-1);
      return param_1;
    }
  }
  FatalError_LocalizedStringId('\0',0xc4,-1);
  return param_1;
}
