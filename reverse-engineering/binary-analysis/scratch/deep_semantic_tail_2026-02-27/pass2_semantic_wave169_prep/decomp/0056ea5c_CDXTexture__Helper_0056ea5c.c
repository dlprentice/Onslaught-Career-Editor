/* address: 0x0056ea5c */
/* name: CDXTexture__Helper_0056ea5c */
/* signature: int __cdecl CDXTexture__Helper_0056ea5c(void * param_1, int param_2) */


int __cdecl CDXTexture__Helper_0056ea5c(void *param_1,int param_2)

{
  uchar *_Str2;
  int iVar1;
  int *piVar2;

  _Str2 = (uchar *)*DAT_009d08dc;
  piVar2 = DAT_009d08dc;
  while( true ) {
    if (_Str2 == (uchar *)0x0) {
      return -((int)piVar2 - (int)DAT_009d08dc >> 2);
    }
    iVar1 = __mbsnbicoll(param_1,_Str2,param_2);
    if ((iVar1 == 0) &&
       ((*(char *)(*piVar2 + param_2) == '=' || (*(char *)(*piVar2 + param_2) == '\0')))) break;
    _Str2 = (uchar *)piVar2[1];
    piVar2 = piVar2 + 1;
  }
  return (int)piVar2 - (int)DAT_009d08dc >> 2;
}
