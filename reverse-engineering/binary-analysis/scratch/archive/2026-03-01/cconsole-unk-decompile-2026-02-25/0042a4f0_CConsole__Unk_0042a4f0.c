/* address: 0x0042a4f0 */
/* name: CConsole__Unk_0042a4f0 */
/* signature: void __thiscall CConsole__Unk_0042a4f0(void * this, void * param_1, int param_2, int param_3) */


void __thiscall CConsole__Unk_0042a4f0(void *this,void *param_1,int param_2,int param_3)

{
  char *line;
  char cVar1;
  int iVar2;
  int iVar3;
  char *pcVar4;

  iVar2 = 0;
  if ((param_2 != 0) && (param_2 == 1)) {
    iVar2 = 1;
  }
  iVar3 = -1;
  line = (char *)((iVar2 + (char)param_1 * 2) * 0x40 + 0x23bc + (int)this);
  pcVar4 = line;
  do {
    if (iVar3 == 0) break;
    iVar3 = iVar3 + -1;
    cVar1 = *pcVar4;
    pcVar4 = pcVar4 + 1;
  } while (cVar1 != '\0');
  if (iVar3 != -2) {
    CConsole__ExecuteCommandLine(this,line);
  }
  return;
}
