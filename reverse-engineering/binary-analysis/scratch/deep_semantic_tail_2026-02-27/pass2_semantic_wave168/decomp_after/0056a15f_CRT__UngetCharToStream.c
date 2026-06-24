/* address: 0x0056a15f */
/* name: CRT__UngetCharToStream */
/* signature: uint __cdecl CRT__UngetCharToStream(uint param_1, void * param_2) */


uint __cdecl CRT__UngetCharToStream(uint param_1,void *param_2)

{
  uint uVar1;

  if ((param_1 != 0xffffffff) &&
     ((uVar1 = *(uint *)((int)param_2 + 0xc), (uVar1 & 1) != 0 ||
      (((uVar1 & 0x80) != 0 && ((uVar1 & 2) == 0)))))) {
    if (*(int *)((int)param_2 + 8) == 0) {
      CRT__InitFileBuffer(param_2);
    }
    if (*(int *)param_2 == *(int *)((int)param_2 + 8)) {
      if (*(int *)((int)param_2 + 4) != 0) {
        return 0xffffffff;
      }
      *(int *)param_2 = *(int *)param_2 + 1;
    }
    if ((*(byte *)((int)param_2 + 0xc) & 0x40) == 0) {
      *(int *)param_2 = *(int *)param_2 + -1;
      **(char **)param_2 = (char)param_1;
    }
    else {
      *(int *)param_2 = *(int *)param_2 + -1;
      if (**(char **)param_2 != (char)param_1) {
        *(char **)param_2 = *(char **)param_2 + 1;
        return 0xffffffff;
      }
    }
    *(int *)((int)param_2 + 4) = *(int *)((int)param_2 + 4) + 1;
    *(uint *)((int)param_2 + 0xc) = *(uint *)((int)param_2 + 0xc) & 0xffffffef | 1;
    return param_1 & 0xff;
  }
  return 0xffffffff;
}
