/* address: 0x00565dc1 */
/* name: CTexture__Helper_00565dc1 */
/* signature: int __cdecl CTexture__Helper_00565dc1(void * param_1, void * param_2) */


int __cdecl CTexture__Helper_00565dc1(void *param_1,void *param_2)

{
  char cVar1;
  size_t _Count;
  char *_Source;
  char *_Dest;

  _Source = param_2;
  _memset(param_1,0,0x88);
  if (*(char *)param_2 != '\0') {
    if ((*(char *)param_2 != '.') || (*(char *)((int)param_2 + 1) == '\0')) {
      param_2 = (void *)0x0;
      while( true ) {
        _Count = CTexture__Helper_0056c060(_Source,&DAT_005e5e30);
        if (_Count == 0) {
          return -1;
        }
        cVar1 = _Source[_Count];
        if (param_2 == (void *)0x0) {
          if (0x3f < (int)_Count) {
            return -1;
          }
          _Dest = param_1;
          if (cVar1 == '.') {
            return -1;
          }
        }
        else if (param_2 == (void *)0x1) {
          if (0x3f < (int)_Count) {
            return -1;
          }
          if (cVar1 == '_') {
            return -1;
          }
          _Dest = (char *)((int)param_1 + 0x40);
        }
        else {
          if (param_2 != (void *)0x2) {
            return -1;
          }
          if ((cVar1 != '\0') && (cVar1 != ',')) {
            return -1;
          }
          _Dest = (char *)((int)param_1 + 0x80);
        }
        _strncpy(_Dest,_Source,_Count);
        if (cVar1 == ',') {
          return 0;
        }
        if (cVar1 == '\0') break;
        param_2 = (void *)((int)param_2 + 1);
        _Source = _Source + _Count + 1;
      }
      return 0;
    }
    CRT__StrCpyAligned((void *)((int)param_1 + 0x80),(void *)((int)param_2 + 1));
  }
  return 0;
}
