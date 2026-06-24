/* address: 0x005d075f */
/* name: CTexture__Helper_005d075f */
/* signature: int __cdecl CTexture__Helper_005d075f(void * param_1, int param_2, void * param_3) */


int __cdecl CTexture__Helper_005d075f(void *param_1,int param_2,void *param_3)

{
  int iVar1;
  undefined1 *local_24;
  int local_20;
  void *local_1c;
  undefined4 local_18;

  local_1c = param_1;
  local_24 = param_1;
  local_18 = 0x42;
  local_20 = param_2;
  iVar1 = CRT__FormatOutputToStream((int)&local_24,param_3,&stack0x00000010);
  local_20 = local_20 + -1;
  if (local_20 < 0) {
    CRT__FlsBuf(0,&local_24);
  }
  else {
    *local_24 = 0;
  }
  return iVar1;
}
