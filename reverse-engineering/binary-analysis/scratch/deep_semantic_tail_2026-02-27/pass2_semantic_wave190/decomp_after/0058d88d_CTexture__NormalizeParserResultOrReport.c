/* address: 0x0058d88d */
/* name: CTexture__NormalizeParserResultOrReport */
/* signature: int __thiscall CTexture__NormalizeParserResultOrReport(void * this, void * param_1, int param_2) */


int __thiscall CTexture__NormalizeParserResultOrReport(void *this,void *param_1,int param_2)

{
  if (param_1 == (void *)0x0) {
    if (*(int *)((int)this + 0x4c) == 0) {
      CTexture__AppendDiagnosticMessage(*(void **)this,(int)this + 0x10,0,0x5ea504);
      *(undefined4 *)((int)this + 0x4c) = 1;
    }
    *(undefined4 *)((int)this + 0x50) = 1;
    param_1 = (void *)0x0;
  }
  return (int)param_1;
}
