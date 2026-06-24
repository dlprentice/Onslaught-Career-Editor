/* address: 0x00599a74 */
/* name: CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag */
/* signature: void __cdecl CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag(int param_1, int param_2, int param_3, int param_4) */


void __cdecl
CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag
          (int param_1,int param_2,int param_3,int param_4)

{
  undefined1 local_104 [255];
  undefined1 local_5;

  CFastVB__Helper_005d070f(local_104,0x100,(void *)param_4,&stack0x00000014);
  local_5 = 0;
  CTexture__Helper_0058c893((void *)(*(int *)(param_1 + 4) + 4),param_2,param_3,0x5ea38c);
  *(undefined4 *)(param_1 + 0x40) = 1;
  return;
}
