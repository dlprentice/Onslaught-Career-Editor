/* address: 0x00568ed7 */
/* name: CDXTexture__Unk_00568ed7 */
/* signature: void CDXTexture__Unk_00568ed7(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Unk_00568ed7(void)

{
  void *pvVar1;
  char *pcVar2;
  int local_c;
  int local_8;

  if (DAT_009d4608 == 0) {
    CDXTexture__Helper_0056836a();
  }
  GetModuleFileNameA((HMODULE)0x0,&DAT_009d09c4,0x104);
  _DAT_009d08ec = &DAT_009d09c4;
  pcVar2 = &DAT_009d09c4;
  if (*DAT_009d35f4 != '\0') {
    pcVar2 = DAT_009d35f4;
  }
  CDXTexture__Unk_00568f70(pcVar2,(void *)0x0,(void *)0x0,&local_8,&local_c);
  pvVar1 = _malloc(local_c + local_8 * 4);
  if (pvVar1 == (void *)0x0) {
    __amsg_exit(8);
  }
  CDXTexture__Unk_00568f70(pcVar2,pvVar1,(void *)((int)pvVar1 + local_8 * 4),&local_8,&local_c);
  _DAT_009d08d4 = pvVar1;
  _DAT_009d08d0 = local_8 + -1;
  return;
}
