(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-44588256"],{"1a23":function(t,e,n){"use strict";n.r(e),n.d(e,"CountUp",(function(){return i}));var a=function(){return(a=Object.assign||function(t){for(var e,n=1,a=arguments.length;n<a;n++)for(var i in e=arguments[n])Object.prototype.hasOwnProperty.call(e,i)&&(t[i]=e[i]);return t}).apply(this,arguments)},i=function(){function t(t,e,n){var i=this;this.target=t,this.endVal=e,this.options=n,this.version="2.0.4",this.defaults={startVal:0,decimalPlaces:0,duration:2,useEasing:!0,useGrouping:!0,smartEasingThreshold:999,smartEasingAmount:333,separator:",",decimal:".",prefix:"",suffix:""},this.finalEndVal=null,this.useEasing=!0,this.countDown=!1,this.error="",this.startVal=0,this.paused=!0,this.count=function(t){i.startTime||(i.startTime=t);var e=t-i.startTime;i.remaining=i.duration-e,i.useEasing?i.countDown?i.frameVal=i.startVal-i.easingFn(e,0,i.startVal-i.endVal,i.duration):i.frameVal=i.easingFn(e,i.startVal,i.endVal-i.startVal,i.duration):i.countDown?i.frameVal=i.startVal-(i.startVal-i.endVal)*(e/i.duration):i.frameVal=i.startVal+(i.endVal-i.startVal)*(e/i.duration),i.countDown?i.frameVal=i.frameVal<i.endVal?i.endVal:i.frameVal:i.frameVal=i.frameVal>i.endVal?i.endVal:i.frameVal,i.frameVal=Math.round(i.frameVal*i.decimalMult)/i.decimalMult,i.printValue(i.frameVal),e<i.duration?i.rAF=requestAnimationFrame(i.count):null!==i.finalEndVal?i.update(i.finalEndVal):i.callback&&i.callback()},this.formatNumber=function(t){var e,n,a,s,r,o=t<0?"-":"";if(e=Math.abs(t).toFixed(i.options.decimalPlaces),a=(n=(e+="").split("."))[0],s=n.length>1?i.options.decimal+n[1]:"",i.options.useGrouping){r="";for(var l=0,c=a.length;l<c;++l)0!==l&&l%3==0&&(r=i.options.separator+r),r=a[c-l-1]+r;a=r}return i.options.numerals&&i.options.numerals.length&&(a=a.replace(/[0-9]/g,(function(t){return i.options.numerals[+t]})),s=s.replace(/[0-9]/g,(function(t){return i.options.numerals[+t]}))),o+i.options.prefix+a+s+i.options.suffix},this.easeOutExpo=function(t,e,n,a){return n*(1-Math.pow(2,-10*t/a))*1024/1023+e},this.options=a({},this.defaults,n),this.formattingFn=this.options.formattingFn?this.options.formattingFn:this.formatNumber,this.easingFn=this.options.easingFn?this.options.easingFn:this.easeOutExpo,this.startVal=this.validateValue(this.options.startVal),this.frameVal=this.startVal,this.endVal=this.validateValue(e),this.options.decimalPlaces=Math.max(this.options.decimalPlaces),this.decimalMult=Math.pow(10,this.options.decimalPlaces),this.resetDuration(),this.options.separator=String(this.options.separator),this.useEasing=this.options.useEasing,""===this.options.separator&&(this.options.useGrouping=!1),this.el="string"==typeof t?document.getElementById(t):t,this.el?this.printValue(this.startVal):this.error="[CountUp] target is null or undefined"}return t.prototype.determineDirectionAndSmartEasing=function(){var t=this.finalEndVal?this.finalEndVal:this.endVal;this.countDown=this.startVal>t;var e=t-this.startVal;if(Math.abs(e)>this.options.smartEasingThreshold){this.finalEndVal=t;var n=this.countDown?1:-1;this.endVal=t+n*this.options.smartEasingAmount,this.duration=this.duration/2}else this.endVal=t,this.finalEndVal=null;this.finalEndVal?this.useEasing=!1:this.useEasing=this.options.useEasing},t.prototype.start=function(t){this.error||(this.callback=t,this.duration>0?(this.determineDirectionAndSmartEasing(),this.paused=!1,this.rAF=requestAnimationFrame(this.count)):this.printValue(this.endVal))},t.prototype.pauseResume=function(){this.paused?(this.startTime=null,this.duration=this.remaining,this.startVal=this.frameVal,this.determineDirectionAndSmartEasing(),this.rAF=requestAnimationFrame(this.count)):cancelAnimationFrame(this.rAF),this.paused=!this.paused},t.prototype.reset=function(){cancelAnimationFrame(this.rAF),this.paused=!0,this.resetDuration(),this.startVal=this.validateValue(this.options.startVal),this.frameVal=this.startVal,this.printValue(this.startVal)},t.prototype.update=function(t){cancelAnimationFrame(this.rAF),this.startTime=null,this.endVal=this.validateValue(t),this.endVal!==this.frameVal&&(this.startVal=this.frameVal,this.finalEndVal||this.resetDuration(),this.determineDirectionAndSmartEasing(),this.rAF=requestAnimationFrame(this.count))},t.prototype.printValue=function(t){var e=this.formattingFn(t);"INPUT"===this.el.tagName?this.el.value=e:"text"===this.el.tagName||"tspan"===this.el.tagName?this.el.textContent=e:this.el.innerHTML=e},t.prototype.ensureNumber=function(t){return"number"==typeof t&&!isNaN(t)},t.prototype.validateValue=function(t){var e=Number(t);return this.ensureNumber(e)?e:(this.error="[CountUp] invalid start or end value: "+t,null)},t.prototype.resetDuration=function(){this.startTime=null,this.duration=1e3*Number(this.options.duration),this.remaining=this.duration},t}()},"1ddb":function(t,e,n){(function(e){(function(e,a){t.exports=a(n("1a23"))})(0,(function(t){"use strict";var n="object"==typeof e&&e&&e.Object===Object&&e,a="object"==typeof self&&self&&self.Object===Object&&self,i=n||a||Function("return this")(),s=i.Symbol,r=Object.prototype,o=r.hasOwnProperty,l=r.toString,c=s?s.toStringTag:void 0;function u(t){var e=o.call(t,c),n=t[c];try{t[c]=void 0}catch(i){}var a=l.call(t);return e?t[c]=n:delete t[c],a}var d=Object.prototype,h=d.toString;function f(t){return h.call(t)}var m="[object Null]",p="[object Undefined]",v=s?s.toStringTag:void 0;function g(t){return null==t?void 0===t?p:m:v&&v in Object(t)?u(t):f(t)}function b(t){var e=typeof t;return null!=t&&("object"==e||"function"==e)}var V="[object AsyncFunction]",_="[object Function]",y="[object GeneratorFunction]",T="[object Proxy]";function x(t){if(!b(t))return!1;var e=g(t);return e==_||e==y||e==V||e==T}var F={__countup__:t.CountUp,name:"ICountUp",props:{endVal:{type:Number,required:!0},options:{type:Object,required:!1}},data:function(){return{instance:null}},watch:{endVal:{handler:function(t){var e=this;e.instance&&x(e.instance.update)&&e.instance.update(t)},deep:!1}},methods:{init:function(){var e=this;if(!e.instance){var n=e.$el,a=new t.CountUp(n,e.endVal,e.options);a.error||(a.start((function(){return e.$emit("ready",a,t.CountUp)})),e.instance=a)}},uninit:function(){var t=this;t.instance=null},printValue:function(t){var e=this;if(e.instance&&x(e.instance.printValue))return e.instance.printValue(t)},start:function(t){var e=this;if(e.instance&&x(e.instance.start)&&x(t))return e.instance.start(t)},pauseResume:function(){var t=this;if(t.instance&&x(t.instance.pauseResume))return t.instance.pauseResume()},reset:function(){var t=this;if(t.instance&&x(t.instance.reset))return t.instance.reset()},update:function(t){var e=this;if(e.instance&&x(e.instance.update))return e.instance.update(t)}},mounted:function(){var t=this;t.init()},beforeDestroy:function(){var t=this;t.uninit()},render:function(t){return t("span",{})}};return F}))}).call(this,n("c8ba"))},4860:function(t,e,n){"use strict";n("6ccc")},"6ccc":function(t,e,n){},b109:function(t,e,n){},e053:function(t,e,n){"use strict";n.d(e,"c",(function(){return i})),n.d(e,"d",(function(){return s})),n.d(e,"e",(function(){return r})),n.d(e,"a",(function(){return o})),n.d(e,"g",(function(){return l})),n.d(e,"h",(function(){return c})),n.d(e,"b",(function(){return u})),n.d(e,"f",(function(){return d}));var a=n("9bd2");function i(t){return Object(a["a"])({url:"/hdfs/getcalltree",method:"GET",params:t})}function s(t){return Object(a["a"])({url:"/hdfs/getfuncfeature",method:"GET",params:t})}function r(t){return Object(a["a"])({url:"/hdfs/gettimeline",method:"GET",params:t})}function o(t){return Object(a["a"])({url:"/hdfs/createtask",method:"GET",params:t})}function l(){return Object(a["a"])({url:"/hdfs/gettasklist",method:"GET"})}function c(t){return Object(a["a"])({url:"/hdfs/refresh",method:"GET",params:t})}function u(t){return Object(a["a"])({url:"/hdfs/delete",method:"GET",params:t})}function d(t){return Object(a["a"])({url:"/hdfs/gettracedetail",method:"GET",params:t})}},e762:function(t,e,n){"use strict";n.r(e);var a=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("d2-container",[n("template",{slot:"header"},[t._v("\n        ASTracer 分析报告\n    ")]),t._v(" "),n("detail"),t._v(" "),n("div",{staticStyle:{"margin-top":"2%"}},[n("el-tabs",{attrs:{type:"border-card"},on:{"tab-click":t.changeTab},model:{value:t.activeTab,callback:function(e){t.activeTab=e},expression:"activeTab"}},[n("el-tab-pane",{attrs:{label:"统计信息",name:"sampler"}},[n("all_func")],1),t._v(" "),n("el-tab-pane",{attrs:{label:"调用树",name:"tree"}},[n("tree")],1),t._v(" "),n("el-tab-pane",{attrs:{label:"时间轴",name:"time"}},[n("el-card",{directives:[{name:"loading",rawName:"v-loading",value:t.loading,expression:"loading"}],attrs:{"element-loading-text":"你需要选择一个函数"}},[n("ve-line",{ref:"timeline",attrs:{data:t.chartData,settings:t.chartSettings,height:"500px"}})],1)],1)],1)],1)],2)},i=[],s=(n("7f7f"),function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",[n("el-button",{attrs:{size:"small",round:""},on:{click:function(e){t.expandAll=!t.expandAll}}},[t._v(t._s(t.expandAll?"Collapse":"Expand"))]),t._v(" "),n("el-button",{attrs:{size:"small",round:""},on:{click:function(e){t.direct=!t.direct}}},[t._v(t._s(t.direct?"Vertical":"Horizontal"))]),t._v(" "),n("el-container",[n("el-main",{staticStyle:{"align-items":"center"}},[n("el-card",{directives:[{name:"loading",rawName:"v-loading",value:t.loading,expression:"loading"}],staticClass:"tree-bg",attrs:{"element-loading-text":"你需要选择一个函数","element-loading-spinner":"el-icon-loading"}},[t.tree?n("el-carousel",{staticClass:"tree-bg",staticStyle:{margin:"2%"},attrs:{height:"500px"}},t._l(t.tree,(function(e,a){return n("el-carousel-item",{key:a},[n("div",{staticClass:"tree-wrapper"},[n("org-tree",{attrs:{data:e,collapsable:"","node-render":t.nodeRender,"expand-all":t.expandAll,horizontal:t.direct,props:t.props}})],1)])})),1):t._e()],1)],1)],1)],1)}),r=[],o=n("9a0d"),l=n.n(o),c=(n("749a"),n("e053")),u={name:"trace-tree",components:{OrgTree:l.a},created:function(){this.selectFunc&&this.getTree()},computed:{selectFunc:{get:function(){return this.$store.state.hdfs.selectFunc},set:function(t){this.$store.commit("hdfs/setSelectFunc",t)}}},data:function(){return{tree:{},loading:!0,expandAll:!0,direct:!0,props:{id:"hash",label:"name",expand:"expand",children:"childs"}}},watch:{selectFunc:function(t){this.getTree()}},methods:{getTree:function(){var t=this;Object(c["c"])({name:this.$store.state.hdfs.currentTaskName,func_name:this.selectFunc}).then((function(e){t.loading=!1,t.tree=e["res"]}))},nodeRender:function(t,e){var n=e.name===this.selectFunc?"danger":"primary";return t("el-button",{attrs:{type:n}},[" ",e.name])}}},d=u,h=(n("4860"),n("2877")),f=Object(h["a"])(d,s,r,!1,null,null,null),m=f.exports,p=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("el-row",{attrs:{gutter:30}},[n("el-col",{attrs:{span:8}},[n("el-card",{staticStyle:{background:"#f0f9eb"}},[n("div",{attrs:{slot:"header"},slot:"header"},[n("d2-icon",{attrs:{name:"file-code-o"}}),t._v(" "),n("span",{staticStyle:{"margin-left":"2%"}},[t._v("文件大小")])],1),t._v(" "),n("div",{staticClass:"iCountUp"},[n("ICountUp",{attrs:{endVal:t.size}}),t._v("\n                MB\n            ")],1)])],1),t._v(" "),n("el-col",{attrs:{span:8}},[n("el-card",{staticStyle:{background:"#f2f2f3"}},[n("div",{attrs:{slot:"header"},slot:"header"},[n("d2-icon",{attrs:{name:"code"}}),t._v(" "),n("span",{staticStyle:{"margin-left":"2%"}},[t._v("函数种类")])],1),t._v(" "),n("div",{staticClass:"iCountUp"},[n("ICountUp",{attrs:{endVal:t.func_type}})],1)])],1),t._v(" "),n("el-col",{attrs:{span:8}},[n("el-card",{staticStyle:{background:"#fdf0f0"}},[n("div",{attrs:{slot:"header"},slot:"header"},[n("d2-icon",{attrs:{name:"code-fork"}}),t._v(" "),n("span",{staticStyle:{"margin-left":"2%"}},[t._v("调用树种类")])],1),t._v(" "),n("div",{staticClass:"iCountUp"},[n("ICountUp",{attrs:{endVal:t.tree_type}})],1)])],1)],1)},v=[],g=n("1ddb"),b=n.n(g),V={name:"detail-info",components:{ICountUp:b.a},created:function(){this.taskName&&this.getData()},data:function(){return{size:0,func_type:0,tree_type:0}},computed:{taskName:{get:function(){return this.$store.state.hdfs.currentTaskName}}},watch:{taskName:function(t){this.getData()}},methods:{getData:function(){var t=this;Object(c["f"])({name:this.taskName}).then((function(e){t.size=e.size,t.func_type=e.func_type,t.tree_type=e.tree_type}))}}},_=V,y=(n("eb74"),Object(h["a"])(_,p,v,!1,null,"4e2d2962",null)),T=y.exports,x=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",[t.funcData?n("el-form",{staticStyle:{margin:"10px"},attrs:{inline:!0,size:"mini"}},[n("el-form-item",{attrs:{label:"data export [ "+t.funcData.length+" ]"}},[n("el-button-group",[n("el-button",{attrs:{type:"primary",size:"mini",disabled:!t.funcData}},[t._v("\n                    xlsx\n                ")]),t._v(" "),n("el-button",{attrs:{type:"primary",size:"mini",disabled:!t.funcData}},[t._v("\n                    csv\n                ")])],1)],1)],1):t._e(),t._v(" "),n("el-table",{directives:[{name:"loading",rawName:"v-loading",value:t.loading,expression:"loading"}],staticStyle:{width:"100%"},attrs:{data:t.funcData,size:"mini",stripe:"","default-sort":{prop:"count",order:"descending"}}},[n("el-table-column",{attrs:{type:"selection",width:"55"}}),t._v(" "),n("el-table-column",{attrs:{prop:"name",label:"function name",width:"250"}}),t._v(" "),n("el-table-column",{attrs:{prop:"count",label:"count",sortable:""},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-tag",[t._v(t._s(e.row.count))])]}}])}),t._v(" "),n("el-table-column",{attrs:{prop:"mean",label:"mean(ms)",sortable:""},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-tag",{attrs:{type:"danger"}},[t._v(t._s(e.row.mean.toFixed(2)))])]}}])}),t._v(" "),n("el-table-column",{attrs:{prop:"std",label:"std"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-tag",{attrs:{type:"success"}},[t._v(t._s(e.row.std.toFixed(2)))])]}}])}),t._v(" "),n("el-table-column",{attrs:{label:"status"},scopedSlots:t._u([{key:"default",fn:function(t){return[t.row.std<t.row.mean?n("span",[n("d2-icon",{staticStyle:{"font-size":"20px","line-height":"32px",color:"#67C23A"},attrs:{slot:"active",name:"thumbs-up"},slot:"active"})],1):n("span",[n("d2-icon",{staticStyle:{"font-size":"20px","line-height":"32px",color:"#F56C6C"},attrs:{slot:"inactive",name:"thumbs-down"},slot:"inactive"})],1)]}}])}),t._v(" "),n("el-table-column",{attrs:{prop:"total",label:"total(ms)",sortable:""},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-tag",{attrs:{type:"info"}},[t._v(t._s(Math.round(e.row.total)))])]}}])}),t._v(" "),n("el-table-column",{attrs:{prop:"min",label:"min(ms)"}}),t._v(" "),n("el-table-column",{attrs:{prop:"50%",label:"median(ms)"}}),t._v(" "),n("el-table-column",{attrs:{prop:"max",label:"max(ms)"}}),t._v(" "),n("el-table-column",{attrs:{label:"operate",width:"200"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-button",{attrs:{size:"mini",type:"info"},on:{click:function(n){t.moveTree(e.row.name)}}},[t._v("call tree\n                ")]),t._v(" "),n("el-button",{attrs:{size:"mini",type:"primary"},on:{click:function(n){t.moveTimeline(e.row.name)}}},[t._v("timeline\n                ")])]}}])})],1)],1)},F=[],k={name:"all-func-info",data:function(){return{funcData:null,loading:!0,funcname:null}},created:function(){this.taskName&&this.getData()},computed:{taskName:{get:function(){return this.$store.state.hdfs.currentTaskName}}},watch:{taskName:function(t){this.getData()}},methods:{moveTree:function(t){this.$store.commit("hdfs/setSelectFunc",t),this.$store.commit("hdfs/setActiveTab","tree")},moveTimeline:function(t){this.$store.commit("hdfs/setSelectFunc",t),this.$store.commit("hdfs/setActiveTab","time")},getData:function(){var t=this;Object(c["d"])({name:this.$store.state.hdfs.currentTaskName}).then((function(e){t.loading=!1,t.funcData=e}))}}},w=k,E=Object(h["a"])(w,x,F,!1,null,"66558651",null),j=E.exports,S={name:"index",components:{tree:m,detail:T,all_func:j},created:function(){var t=this.$store.state.hdfs.currentTaskName;""===t?(this.$router.push({name:"history"}),this.$notify({title:"注意",message:"请选择或创建task",type:"warning"})):this.selectFunc&&(this.getChartData(),this.loading=!1)},data:function(){return{activeName:"sampler",chartData:{},loading:!0,chartSettings:{stack:{func:["all"]},area:!0}}},computed:{activeTab:{get:function(){return this.$store.state.hdfs.activeTab},set:function(t){this.$store.commit("hdfs/setActiveTab",t)}},selectFunc:function(){return this.$store.state.hdfs.selectFunc}},methods:{changeTab:function(t){this.activeTab=t.name},getChartData:function(){var t=this;Object(c["e"])({name:this.$store.state.hdfs.currentTaskName,count:100,func_name:this.selectFunc}).then((function(e){t.chartData=e}))}},watch:{activeTab:function(t){var e=this;"time"===t&&this.$nextTick((function(t){e.$refs["timeline"].echarts.resize()}))},selectFunc:function(t){this.getChartData(),this.loading=!1}}},D=S,A=Object(h["a"])(D,a,i,!1,null,null,null);e["default"]=A.exports},eb74:function(t,e,n){"use strict";n("b109")}}]);
//# sourceMappingURL=chunk-44588256.7b78c951.js.map