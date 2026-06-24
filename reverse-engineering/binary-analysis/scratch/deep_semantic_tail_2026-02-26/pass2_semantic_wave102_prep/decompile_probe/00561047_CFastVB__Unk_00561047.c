/* address: 0x00561047 */
/* name: CFastVB__Unk_00561047 */
/* signature: void __cdecl CFastVB__Unk_00561047(void * param_1, void * param_2, int param_3, int param_4) */


void __cdecl CFastVB__Unk_00561047(void *param_1,void *param_2,int param_3,int param_4)

{
  int iVar1;
  char *pcVar2;
  char *pcVar3;
  undefined1 local_2c [24];
  int local_14;
  int local_10;

  CFastVB__Helper_00569b4c
            ((int)*(undefined8 *)param_1,(int)((ulonglong)*(undefined8 *)param_1 >> 0x20),&local_14,
             local_2c);
  iVar1 = local_10 + -1;
  pcVar2 = (char *)((uint)(local_14 == 0x2d) + (int)param_2);
  CFastVB__Helper_00569ad5(pcVar2,param_3,(int)&local_14);
  local_10 = local_10 + -1;
  if ((local_10 < -4) || (param_3 <= local_10)) {
    CFastVB__Unk_00560e89(param_2,param_3,param_4,&local_14,1);
  }
  else {
    if (iVar1 < local_10) {
      do {
        pcVar3 = pcVar2;
        pcVar2 = pcVar3 + 1;
      } while (*pcVar3 != '\0');
      pcVar3[-1] = '\0';
    }
    CFastVB__Unk_00560fa0(param_2,param_3,&local_14,1);
  }
  return;
}
