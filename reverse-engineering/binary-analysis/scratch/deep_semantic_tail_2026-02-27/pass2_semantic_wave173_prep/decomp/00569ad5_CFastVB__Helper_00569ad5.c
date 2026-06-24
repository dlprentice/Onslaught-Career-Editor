/* address: 0x00569ad5 */
/* name: CFastVB__Helper_00569ad5 */
/* signature: void __cdecl CFastVB__Helper_00569ad5(void * param_1, int param_2, int param_3) */


void __cdecl CFastVB__Helper_00569ad5(void *param_1,int param_2,int param_3)

{
  char *_Str;
  void *pvVar1;
  char *pcVar2;
  size_t sVar3;
  char *pcVar4;
  char cVar5;

  pvVar1 = param_1;
  pcVar4 = *(char **)(param_3 + 0xc);
  _Str = (char *)((int)param_1 + 1);
  *(undefined1 *)param_1 = 0x30;
  pcVar2 = _Str;
  if (0 < param_2) {
    param_1 = (void *)param_2;
    param_2 = 0;
    do {
      cVar5 = *pcVar4;
      if (cVar5 == '\0') {
        cVar5 = '0';
      }
      else {
        pcVar4 = pcVar4 + 1;
      }
      *pcVar2 = cVar5;
      pcVar2 = pcVar2 + 1;
      param_1 = (void *)((int)param_1 + -1);
    } while (param_1 != (void *)0x0);
  }
  *pcVar2 = '\0';
  if ((-1 < param_2) && ('4' < *pcVar4)) {
    while (pcVar2 = pcVar2 + -1, *pcVar2 == '9') {
      *pcVar2 = '0';
    }
    *pcVar2 = *pcVar2 + '\x01';
  }
  if (*(char *)pvVar1 == '1') {
    *(int *)(param_3 + 4) = *(int *)(param_3 + 4) + 1;
  }
  else {
    sVar3 = _strlen(_Str);
    CRT__MemMoveOverlapSafe(pvVar1,_Str,sVar3 + 1);
  }
  return;
}
