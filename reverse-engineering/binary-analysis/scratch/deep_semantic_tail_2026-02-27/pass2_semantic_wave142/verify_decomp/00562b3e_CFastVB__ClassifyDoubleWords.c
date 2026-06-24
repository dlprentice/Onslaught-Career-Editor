/* address: 0x00562b3e */
/* name: CFastVB__ClassifyDoubleWords */
/* signature: int __cdecl CFastVB__ClassifyDoubleWords(int param_1, uint param_2) */


int __cdecl CFastVB__ClassifyDoubleWords(int param_1,uint param_2)

{
  int iStack_8;

  if (param_2 == 0x7ff00000) {
    if (param_1 == 0) {
      return 1;
    }
  }
  else if ((param_2 == 0xfff00000) && (param_1 == 0)) {
    return 2;
  }
  if ((param_2._2_2_ & 0x7ff8) == 0x7ff8) {
    iStack_8 = 3;
  }
  else {
    if (((param_2._2_2_ & 0x7ff8) != 0x7ff0) || (((param_2 & 0x7ffff) == 0 && (param_1 == 0)))) {
      return 0;
    }
    iStack_8 = 4;
  }
  return iStack_8;
}
