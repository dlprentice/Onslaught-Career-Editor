/* address: 0x00592d45 */
/* name: CDXTexture__Helper_00592d45 */
/* signature: void __stdcall CDXTexture__Helper_00592d45(void * param_1, int param_2) */


void CDXTexture__Helper_00592d45(void *param_1,int param_2)

{
  if (*(code **)((int)param_1 + 0x40) != (code *)0x0) {
    (**(code **)((int)param_1 + 0x40))(param_1,param_2);
  }
                    /* WARNING: Subroutine does not return */
  _longjmp(param_1,1);
}
