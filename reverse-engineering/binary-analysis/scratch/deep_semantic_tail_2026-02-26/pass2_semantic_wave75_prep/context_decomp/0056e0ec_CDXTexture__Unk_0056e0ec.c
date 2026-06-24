/* address: 0x0056e0ec */
/* name: CDXTexture__Unk_0056e0ec */
/* signature: void __cdecl CDXTexture__Unk_0056e0ec(uint param_1, void * param_2, uint param_3, int param_4) */


void __cdecl CDXTexture__Unk_0056e0ec(uint param_1,void *param_2,uint param_3,int param_4)

{
  ulonglong uVar1;
  char *pcVar2;
  char *pcVar3;
  char cVar4;

  pcVar2 = param_2;
  if (param_4 != 0) {
    *(undefined1 *)param_2 = 0x2d;
    param_2 = (void *)((int)param_2 + 1);
    param_1 = -param_1;
    pcVar2 = param_2;
  }
  do {
    pcVar3 = pcVar2;
    uVar1 = (ulonglong)param_1;
    param_1 = param_1 / param_3;
    cVar4 = (char)(uVar1 % (ulonglong)param_3);
    if ((uint)(uVar1 % (ulonglong)param_3) < 10) {
      cVar4 = cVar4 + '0';
    }
    else {
      cVar4 = cVar4 + 'W';
    }
    *pcVar3 = cVar4;
    pcVar2 = pcVar3 + 1;
  } while (param_1 != 0);
  pcVar3[1] = '\0';
  do {
    cVar4 = *pcVar3;
    *pcVar3 = *(char *)param_2;
    *(char *)param_2 = cVar4;
    pcVar3 = pcVar3 + -1;
    param_2 = (void *)((int)param_2 + 1);
  } while (param_2 < pcVar3);
  return;
}
